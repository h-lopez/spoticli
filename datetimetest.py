from datetime import datetime, timedelta

current_time = datetime.now()
future = current_time + timedelta(minutes=45)
print(current_time)
print(future)
print(future > current_time)
