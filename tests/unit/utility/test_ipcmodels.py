import pytest
import json
from utility.ipcmodels import RedisMessage, RedisRequest, RedisResponse, ReturnWhen

class TestIPCModels:
    def test_return_when_enum(self):
        assert ReturnWhen.FIRST.value == 'first'
        assert ReturnWhen.ALL.value == 'all'

    def test_redis_message_with_dict_data(self):
        data = {"key": "value"}
        message = RedisMessage(
            type="test",
            pattern=None,
            channel="test_channel",
            data=data
        )
        assert message.type == "test"
        assert message.channel == "test_channel"
        assert message.data == data

    def test_redis_message_with_json_string_data(self):
        data_dict = {"key": "value"}
        json_string = json.dumps(data_dict)
        message = RedisMessage(
            type="test",
            pattern=None,
            channel="test_channel",
            data=json_string
        )
        assert message.data == data_dict

    def test_redis_message_with_int_data(self):
        message = RedisMessage(
            type="test",
            pattern=None,
            channel="test_channel",
            data=42
        )
        assert message.data == 42

    def test_redis_request_default_nonce(self):
        request = RedisRequest(data={"test": "data"})
        assert request.data == {"test": "data"}
        assert isinstance(request.nonce, str)
        assert len(request.nonce) > 0

    def test_redis_request_custom_nonce(self):
        custom_nonce = "custom-nonce-123"
        request = RedisRequest(nonce=custom_nonce, data={"test": "data"})
        assert request.nonce == custom_nonce

    def test_redis_response(self):
        data = {"result": "success"}
        response = RedisResponse(data=data)
        assert response.data == data

    def test_redis_response_none_data(self):
        response = RedisResponse(data=None)
        assert response.data is None
