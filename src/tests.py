import creeps.worker

def __pragma__(*args, **kwargs):
    pass

for size, body in creeps.worker.RemoteCarrier.body_composition.items():
    print(size,body)