from mongoengine import signals

post_modify = signals._signals.signal("post_modify")
non_db_signal = signals._signals.signal("non-db-signal")
