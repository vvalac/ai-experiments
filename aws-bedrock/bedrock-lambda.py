import boto3
import botocore.config
import json
from datetime import datetime

def generate_code(message: str, language: str) -> str:
    
    model_id = "meta.llama3-8b-instruct-v1:0"

    prompt_text = f"""
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>

    You are a helpful AI assistant that generates code in {language}.
    Do not add any additional text to your response.
    Only generate the code needed to satisfy the user request.
    
    <|eot_id|><|start_header_id|>user<|end_header_id|>

    {message}
    
    <|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """
    
    body = {
        "prompt": prompt_text,
        "max_gen_len": 512,
        "temperature":0.2,
        "top_p":0.2
    }
    
    try:
        bedrock = boto3.client(
            "bedrock-runtime",
            region_name="us-east-1",
            config=botocore.config.Config(
                read_timeout=120,
                retries={'max_attempts':3}
                )
            )
            
        response = bedrock.invoke_model(
            modelId = model_id,
            body = json.dumps(body)
        )

    except Exception as e:
        print(f"Error generating code: {e}")
        return e
    
    response_content = response.get("body").read().decode('utf-8')
    response_data = json.loads(response_content)

    code = response_data["generation"].strip()
    
    return code
        
def save_code_to_s3_bucket(code, s3_bucket, s3_key):
    s3 = boto3.client("s3")
    
    try:
        s3.put_object(Bucket = s3_bucket, Key = s3_key, Body = code)
        print(f"Code saved to s3: {s3_bucket}")
        
    except Exception as e:
        print(f"Error saving to s3: {e}")
        
        
def lambda_handler(event, context):
    try:
        event_body = json.loads(event['body'])
        message = event_body["message"]
        language = event_body["language"]
        extension = ''
        
        if not language:
            language = 'python'
            
        if language == 'javascript':
            extension = 'js'
        else:
            extension = 'py'
        
        generated_code = generate_code(message, language)
        
        if generated_code:
            current_time = datetime.now().strftime('%H%M%S')
            s3_key = f"code-output/{current_time}.{extension}"
            s3_bucket = "bedrock-bucket-adamsc"
            
            save_code_to_s3_bucket(generated_code, s3_bucket, s3_key)
        else:
            print("No code was generated.")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Code Generation is Complete.')
        }
    
    except Exception as e:
        print(f"Exception in the handler: {e}")
        return {
            'statusCode': 404,
            'body': json.dumps('Code was not generated.')
        }