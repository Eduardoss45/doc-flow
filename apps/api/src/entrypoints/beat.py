import sys
from celery.bin.beat import beat
from src.workers.celery_app import celery
from src.app.config import config


def main():
    print(f"[Beat] Iniciando Celery Beat | TZ: {config.TIMEZONE}")

    # Use o comando beat com o app já injetado
    beat_cmd = beat(app=celery)  # ← passe o app aqui!

    argv = [
        "beat",  # nome do comando (obrigatório)
        "--loglevel=info",
        # Adicione mais flags se quiser:
        # "--scheduler=celery.beat:PersistentScheduler",
        # "--max-interval=300",
    ]

    try:
        beat_cmd.execute_from_commandline(argv)
    except KeyboardInterrupt:
        print("[Beat] Encerrado pelo usuário (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"[Beat] Erro crítico ao iniciar Beat: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
