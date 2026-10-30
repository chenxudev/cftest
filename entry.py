from workers import WorkerEntrypoint

from router import dispatch, load_controllers


load_controllers()


class Default(WorkerEntrypoint):
    async def on_fetch(self, request):
        return await dispatch(request, self.env)
