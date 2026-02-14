import sys
from src.workers.celery_app import celery


def main():
    """
    Ponto de entrada para rodar o Celery Worker
    """
    sys.argv[0] = "celery worker"
    worker_args = ["worker", "--loglevel=info", "--pool=solo"]

    try:
        print("[Worker] Iniciando Celery Worker...")
        celery.worker_main(worker_args)
    except KeyboardInterrupt:
        print("[Worker] Encerrado pelo usuário (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"[Worker] Erro ao iniciar worker: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
