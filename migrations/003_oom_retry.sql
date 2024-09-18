--- add columns oomed and retry_count to the jobs table default them to 0
ALTER TABLE jobs ADD COLUMN oomed BOOLEAN DEFAULT FALSE;
ALTER TABLE jobs ADD COLUMN retry_count INTEGER DEFAULT 0;
