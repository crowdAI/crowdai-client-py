class CrowdAIEvents(object):
    Event = {
        "" : "CrowdAI.Event",
        "SUCCESS" : "CrowdAI.Event.SUCCESS",
        "ERROR" : "CrowdAI.Event.ERROR"
    },
    Connection = {
        "":"CrowdAI.Event.Connection",
        "BEGIN":"CrowdAI.Event.Connection.BEGIN",
        "CONNECTED":"CrowdAI.Event.Connection.CONNECTED",
        "DISCONNECTED": "CrowdAI.Event.Connection.DISCONNECTED",
        "RECONNECTED": "CrowdAI.Event.Connection.RECONNECTED"
    }
    Authentication={
        "":"CrowdAI.Event.Authentication",
        "SUCCESS":"CrowdAI.Event.Authentication.SUCCESS",
        "ERROR":"CrowdAI.Event.Authentication.ERROR"
    }
    Job={
        "":"CrowdAI.Event.Job",
        "ENQUEUED":"CrowdAI.Event.Job.ENQUEUED",
        "WAITING":"CrowdAI.Event.Job.WAITING",
        "RUNNING":"CrowdAI.Event.Job.RUNNING",
        "PROGRESS_UPDATE":"CrowdAI.Event.Job.PROGRESS_UPDATE",
        "COMPLETE":"CrowdAI.Event.Job.COMPLETE",
        "ERROR":"CrowdAI.Event.Job.ERROR",
        "INFO":"CrowdAI.Event.Job.INFO",
        "TIMEOUT":"CrowdAI.Event.Job.TIMEOUT",
    }
    Misc={
        "":"CrowdAI.Event.Misc",
        "FILE_UPLOAD":"CrowdAI.Event.Misc.FILE_UPLOAD"
    }
