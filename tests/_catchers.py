from functools import wraps
from asyncio import iscoroutinefunction, run
from datetime import datetime
from timeit import timeit

class TestFunction:
    def __init__(self,command,**kwargs):
        self.write_to_log = kwargs.get("log") or False
        self.funct = command
        
    @property
    def asynchronous(self):
        if iscoroutinefunction(self.funct):
            return True

        
    async def invoke(self,*args,**kwargs):
        
        def wrap_invoke(funct):
            @wraps(funct)
            async def wrapped(*args,**kwargs):
                works = None
                try:
                    if self.asynchronous:
                        start = timeit()
                        works = await funct(*args,**kwargs)
                        end = timeit()
                        print(f"Execution time: {end-start}")
                    else:
                        start = timeit()
                        works = funct(*args,**kwargs)
                        end = timeit()
                        print(f"Execution time: {end-start}")
                except Exception as e:
                    print(f"test '{funct.__name__}' raised an error {e}")
                    if self.write_to_log:
                        with open("test_log.cblog","a") as appendable:
                            appendable.write(f"{funct.__name__} raised error {e} at time {datetime.now()}")
                    
                return works
            return wrapped
        to_run = wrap_invoke(funct=self.funct)
        
        await to_run(*args,**kwargs)


    def __call__(self,*args,**kwargs): #replaces defualt __call__ with TestFunction.invoke, simulating a standard function call
        result = run(self.invoke(*args,**kwargs))
        return result

def Test(*,log:bool=False): #decorator to bundle functions into class 'TestFunction' so we can easily test success and execution time
    def wrap(cmd):
        return TestFunction(cmd,log=log) 
    return wrap
