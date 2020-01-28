from celery import bootsteps
from kombu import Exchange, Queue

from cern_search_rest_api.config import FILES_PROCESSOR_QUEUE_DLX, FILES_PROCESSOR_EXCHANGE_DLX


class DeclareDeadletter(bootsteps.StartStopStep):
    """
    Celery Bootstep to declare the DLX and DLQ before the worker starts
    processing tasks.
    """
    requires = {'celery.worker.components:Pool'}

    def start(self, worker):
        dlx_exchange = Exchange(FILES_PROCESSOR_EXCHANGE_DLX, type='direct')

        files_processor_dlx = Queue(
            name=FILES_PROCESSOR_QUEUE_DLX,
            exchange=dlx_exchange,
            routing_key=FILES_PROCESSOR_QUEUE_DLX
        )

        with worker.app.pool.acquire() as conn:
            files_processor_dlx.bind(conn).declare()
