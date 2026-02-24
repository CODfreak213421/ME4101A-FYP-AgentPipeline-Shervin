# Starting Project 

### Starting python venv 

CD into directory: 

```cd C:\Users\rockv\Desktop\NUS\NUS Y3S1\FYP\EXPERIMENT 2 Codes\AgentPipeline```

and run

```venv\Scripts\Activate```

### Open Ubuntu to start redis server 

```redis-server``` 

and the port 6379 should be shown 

### Starting celery worker 
In a new terminal, cd in to directory,

Activate virtual environment,

and Run one of the following for windows 

```celery -A proj worker -P solo```

```celery -A proj worker -P threads```

```celery -A proj worker -P gevent```

To get event and logging info

```celery -A proj worker -P threads -E -l info```