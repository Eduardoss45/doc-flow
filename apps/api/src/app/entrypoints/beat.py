import sys
from celery.bin.beat import beat
from workers.celery_app import celery
from app.config import config


def main():
    print(f"[Beat] Iniciando Celery Beat | TZ: {config.TIMEZONE}")

    beat_cmd = beat(app=celery)

    argv = [
        "beat",
        "--loglevel=info",
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
