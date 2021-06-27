from bentoml.saved_bundle import load_from_dir


def test(event, context):
    print('Loading from dir...')
    bservice = load_from_dir('./')
    b_service_api = bservice.get_inference_api('predict')
    print('loaded API: ', b_service_api.name)

    print('Event: ', event)
    prediction = b_service_api.handle_aws_lambda_event(event)
    print(prediction['body'], prediction['statusCode'])
    return prediction
