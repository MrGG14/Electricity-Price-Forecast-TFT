

import  scipy.signal.signaltools
import numpy as np

def _centered(arr, newsize):
    # Return the center newsize portion of the array.
    newsize = np.asarray(newsize)
    currsize = np.array(arr.shape)
    startind = (currsize - newsize) // 2
    endind = startind + newsize
    myslice = [slice(startind[k], endind[k]) for k in range(len(endind))]
    return arr[tuple(myslice)]

scipy.signal.signaltools._centered = _centered

import pandas as pd
from pytorch_forecasting.models.temporal_fusion_transformer.tuning import optimize_hyperparameters
from pytorch_forecasting import TemporalFusionTransformer
import lightning.pytorch as pl
import torch
from pytorch_forecasting.metrics import MAE, SMAPE, PoissonLoss, QuantileLoss
from lightning.pytorch.tuner import Tuner
from  scipy.signal.signaltools import _centered

def get_best_lr(train, train_dataloader, val_dataloader, max_lr=10.0, min_lr=1e-6, **kwargs):

    trainer = pl.Trainer(
        accelerator="gpu" if torch.cuda.is_available() else "cpu",
        # clipping gradients is a hyperparameter and important to prevent divergance
        # of the gradient for recurrent neural networks
        gradient_clip_val=kwargs.get('gradient_clip_val', 0.1),
)
    tft = TemporalFusionTransformer.from_dataset(
        train,
        learning_rate=kwargs.get('learning_rate', 0.15),
        hidden_size=kwargs.get('hidden_size', 16),
        attention_head_size=kwargs.get('attention_head_size', 2),
        dropout=kwargs.get('dropout', 0.1),
        hidden_continuous_size=kwargs.get('hidden_continuous_size', 8),
        loss=kwargs.get('loss', QuantileLoss()),
        log_interval=kwargs.get('log_interval', 10),
        optimizer=kwargs.get('optimizer', "Ranger"),
        reduce_on_plateau_patience=kwargs.get('reduce_on_plateau_patience', 4),
    )

    print(f"Number of parameters in network: {tft.size()/1e3:.1f}k")

    
    res = Tuner(trainer).lr_find(
        tft,
        train_dataloaders=train_dataloader,
        val_dataloaders=val_dataloader,
        max_lr=max_lr,
        min_lr=min_lr,
    )

    print(f"suggested learning rate: {res.suggestion()}")
    fig = res.plot(show=True, suggest=True)
    fig.show()

    return res.suggestion()


def tft_trainer(train, train_dataloader, val_dataloader, max_epochs=20, model_path=None, **kwargs):
    # Filtrar los callbacks que no son None
    trainer = pl.Trainer(
        max_epochs=max_epochs,
        accelerator="gpu" if torch.cuda.is_available() else "cpu",
        enable_model_summary=True,
        gradient_clip_val=kwargs.get('gradient_clip_val', 0.1),
        limit_train_batches=64,
        callbacks = [callback for callback in [kwargs.get('lr_logger'), kwargs.get('early_stop_callback')] if callback is not None]
    )
    
    # Pasar hidden_size y attention_head_size a TemporalFusionTransformer.from_dataset() si están presentes en kwargs
    tft = TemporalFusionTransformer.from_dataset(
        train,
        learning_rate=kwargs.get('learning_rate', 0.15),
        hidden_size=kwargs.get('hidden_size', 16),
        attention_head_size=kwargs.get('attention_head_size', 2),
        dropout=kwargs.get('dropout', 0.1),
        hidden_continuous_size=kwargs.get('hidden_continuous_size', 8),
        loss=kwargs.get('loss', QuantileLoss()),
        log_interval=kwargs.get('log_interval', 10),
        optimizer=kwargs.get('optimizer', "Ranger"),
        reduce_on_plateau_patience=kwargs.get('reduce_on_plateau_patience', 4),
    )

    trainer.fit(tft, train_dataloader, val_dataloader)
    
    # Guardar el modelo entrenado
    if model_path:
        model_path = model_path
        torch.save(tft.state_dict(), model_path)

    loss = trainer.callback_metrics['val_loss'].item() if 'train_loss_epoch' in trainer.callback_metrics else None

    print(f"Number of parameters in network: {tft.size()/1e3:.1f}k")

    return tft, loss



def tft_predict(tft, data, n_preds=None):
    predictions = tft.predict(data, mode="raw", return_x=True)
    
    for idx in range(n_preds if n_preds is not None else predictions.output[0].shape[0]):  # plot n_preds or  all
        tft.plot_prediction(predictions.x, predictions.output, idx=idx, add_loss_to_title=True)



def run_hyperparameter_optimization(train, train_dataloader, val_dataloader, train_model=True, save_model_path=None, n_trials=25, max_epochs=20, model_path="optuna_test", **kwargs):  # el path debe tener extensión .pth
    # Argumentos predeterminados
    default_kwargs = {
        "gradient_clip_val_range": (0.01, 1.0),
        "hidden_size_range": (8, 128),
        "hidden_continuous_size_range": (8, 128),
        "attention_head_size_range": (1, 4),
        "learning_rate_range": (0.001, 0.2),
        "dropout_range": (0.1, 0.3),
        "trainer_kwargs": dict(limit_train_batches=30),
        "reduce_on_plateau_patience": 4,
        "use_learning_rate_finder": False
    }
    
    # Combinar argumentos predeterminados con los proporcionados
    kwargs = {**default_kwargs, **kwargs}
    
    # Crear el estudio de optimización de hiperparámetros
    study = optimize_hyperparameters(train_dataloader, val_dataloader, model_path=model_path, n_trials=n_trials, max_epochs=max_epochs, **kwargs)
    

    # Obtener los mejores hiperparámetros
    print(f'Mejores hiperparámetros hallados: {study.best_trial.params}')
    best_hyperparameters = study.best_trial.params

    grid_tft = None
    if train_model:
        print('########## ENTRENAR MODELO CON MEJORES HIPERPARÁMETROS ###############')
        # Configurar el entrenador
        trainer = pl.Trainer(
            max_epochs=max_epochs,
            accelerator="gpu" if torch.cuda.is_available() else "cpu",
            enable_model_summary=True,
            gradient_clip_val=best_hyperparameters['gradient_clip_val'],
            **kwargs.get("trainer_kwargs", {})  # Agregar argumentos de entrenador opcionales
        )
        
        # Configurar TemporalFusionTransformer
        grid_tft = TemporalFusionTransformer.from_dataset(
            train,
            learning_rate=best_hyperparameters['learning_rate'],
            hidden_size=best_hyperparameters['hidden_size'],
            attention_head_size=best_hyperparameters['attention_head_size'],
            dropout=best_hyperparameters['dropout'],
            hidden_continuous_size=best_hyperparameters['hidden_continuous_size'],
            loss=QuantileLoss(),
            optimizer="Ranger"
        )
        
        # Entrenar el modelo con los datos de entrenamiento
        trainer.fit(grid_tft, train_dataloader, val_dataloader)
        
        if save_model_path:
            # Guardar el modelo entrenado
            torch.save(grid_tft.state_dict(), save_model_path)

    return study, grid_tft

def save_exp_results(exp_path, tft_params, model_days, n_prev_hours, group, val_loss, epochs):
    tft_exps = pd.read_excel(exp_path)

    model_name = f'simple_{group}_{model_days}_{n_prev_hours}'
    loss = val_loss

    new_exp = {'model_name': model_name, 'loss': loss, 'epochs': epochs}
    new_exp.update(tft_params)
    tft_exps = tft_exps.append(new_exp, ignore_index=True)
    tft_exps.to_excel(exp_path, index=False)

