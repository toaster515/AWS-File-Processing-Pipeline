import json
import uuid
from app.services.queue.sqs_service import SQSservice

def handle_process_request(record_id, object_key, bucket, metadata):
    if metadata['mime_type'] != "application/pdf":
        return {"Message":"processing is only supported for PDF files"}
    
    record_ids = []
    if "split_params" in metadata["process_params"]:
        for p in metadata["process_params"]["split_params"]["file_map"]:
            idx = uuid.uuid4()
            record_ids.append(idx)
            metadata["process_params"]["split_params"]["file_map"][p]["id"] = idx
            
    sqs = SQSservice()
    process_request = {
        "record_id": record_id,
        "key": object_key,
        "bucket": bucket,
        "metadata": metadata                
    }
    process_id = sqs.send_message(json.dumps(process_request))


    return {"Message":"Process request submitted successfully", "process_id":process_id, "record_ids":record_ids}
