import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import json
import numpy as np

from tensorflow_serving.apis import classification_pb2
from tensorflow_serving.apis import get_model_metadata_pb2
from tensorflow_serving.apis import get_model_status_pb2
from tensorflow_serving.apis import inference_pb2
from tensorflow_serving.apis import input_pb2
from tensorflow_serving.apis import model_pb2
from tensorflow_serving.apis import model_management_pb2
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import regression_pb2

from tensorflow_serving.config import file_system_storage_path_source_pb2
from tensorflow_serving.config import log_collector_config_pb2
from tensorflow_serving.config import logging_config_pb2
from tensorflow_serving.config import model_server_config_pb2

from tensorflow.core.example import example_pb2
from tensorflow.core.example import feature_pb2

from tensorflow import make_tensor_proto

### ClassificationRequest ###

def gen_ClassificationRequest(
        depth: int = 1,
        args: dict = {}
):
    name = 'ClassificationRequest'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = classification_pb2.ClassificationRequest()

    # model_spec #
    field = 'model_spec'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.model_spec.CopyFrom( gen_ModelSpec(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (ModelSpec) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.model_spec.CopyFrom( gen_ModelSpec(depth + 1) )

    # input #
    field = 'input'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.input.CopyFrom( gen_Input(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (Input) field? (Yes: any | No 'n'): ")
        message.input.CopyFrom( gen_Input(depth + 1) )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### Example ###

def gen_Example(
        depth: int = 1,
        args: dict = {}
):
    name = 'Example'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = example_pb2.Example()

    # features #
    field = 'features'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.features.CopyFrom( gen_Features(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (Features) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            while True:
                message.features.CopyFrom( gen_Features(depth + 1) )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### ExampleList ###

def gen_ExampleList(
        depth: int = 1,
        args: dict = {}
):
    name = 'ExampleList'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = input_pb2.ExampleList()

    # examples #
    field = 'examples'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        for element in args[field]:
            submessage = message.examples.add()
            submessage.CopyFrom( gen_Example(depth + 1, element))
    else:
        answer = input(f"{indent} Add '{field}' (repeated Example) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            while True:
                answer = input(f"{indent}   Add element to '{field}'? (Yes: any | No 'n'): ")
                if answer == 'n':
                    break

                submessage = message.examples.add()
                submessage.CopyFrom( gen_Example(depth + 1) )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### ExampleListWithContext ###

def gen_ExampleListWithContext(
        depth: int = 1,
        args: dict = {}
):
    name = 'ExampleListWithContext'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = input_pb2.ExampleListWithContext()

    # examples #
    field = 'examples'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        for element in args[field]:
            submessage = message.examples.add()
            submessage.CopyFrom( gen_Example(depth + 1, element))
    else:
        answer = input(f"{indent} Add '{field}' (repeated Example) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            while True:
                answer = input(f"{indent}   Add element to '{field}'? (Yes: any | No 'n'): ")
                if answer == 'n':
                    break

                submessage = message.examples.add()
                submessage.CopyFrom( gen_Example(depth + 1) )

    # context #
    field = 'context'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.context.CopyFrom( gen_Example(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (Example) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.context.CopyFrom( gen_Example(depth + 1) )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### Feature ###

def gen_Feature(
        depth: int = 1,
        args: dict = {}
):
    name = 'Feature'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = feature_pb2.Feature()

    # kind #
    field = 'kind'
    if field in args:
        if 'bytes_list' in args[field]:
            print(f"{indent} Setting 'bytes_list' from args...")
            message.bytes_list.value.extend(args[field]['bytes_list'])
        if 'float_list' in args[field]:
            print(f"{indent} Setting 'float_list' from args...")
            message.float_list.value.extend(args[field]['float_list'])
        if 'int64_list' in args[field]:
            print(f"{indent} Setting 'int64_list' from args...")
            message.int64_list.value.extend(args[field]['int64_list'])
    else:
        answer = input(f"{indent} Add '{field}' (oneof) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            oneof_menu = (f"{indent} Available fields:\n"
                          f"{indent}   1.bytes_list (string)\n"
                          f"{indent}   2.float_list (list[float])\n"
                          f"{indent}   2.int64_list (list[int64])\n"
                          f"{indent} Choose a field: ")
            answer = int( input(oneof_menu) )
            if answer == 1:
                bytes_list = input(f"{indent}   Input 'bytes_list': ")
                message.bytes_list.value.extend(bytes_list)
            if answer == 2:
                float_list_as_string = input(f"{indent}   Input 'float_list': ")
                float_list = json.loads(float_list_as_string)
                message.float_list.value.extend(float_list)
            if answer == 3:
                int64_list_as_string = input(f"{indent}   Input 'int64_list': ")
                int64_list = json.loads(int64_list_as_string)
                message.int64_list.value.extend(int64_list)

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### Features ###

def gen_Features(
        depth: int = 1,
        args: dict = {}
):
    name = 'Features'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = feature_pb2.Features()

    # feature #
    field = 'feature'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        for key in args[field]:
            feature = gen_Feature(depth + 1, args[field][key])
            message.feature[key].CopyFrom(feature)
    else:
        answer = input(f"{indent} Add '{field}' (map<string, Feature>) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            while True:
                answer = input(f"{indent}   Add element to '{field}'? (Yes: any | No 'n'): ")
                if answer == 'n':
                    break

                element_key = input(f"{indent}     Input element key (string): ")
                element_value = gen_Feature(depth + 1)
                message.feature[element_key].CopyFrom(element_value)

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### GetModelMetadataRequest ###

def gen_GetModelMetadataRequest(
        depth: int = 1,
        args: dict = {}
):
    name = 'GetModelMetadataRequest'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = get_model_metadata_pb2.GetModelMetadataRequest()

    # model_spec #
    field = 'model_spec'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.model_spec.CopyFrom( gen_ModelSpec(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (ModelSpec) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.model_spec.CopyFrom( gen_ModelSpec(depth + 1) )

    # metadata_field #
    field = 'metadata_field'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.metadata_field.extend( args[field] )
    else:
        answer = input(f"{indent} Add '{field}' (repeated string) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            while True:
                answer = input(f"{indent}   Add element to '{field}'? (Yes: any | No 'n'): ")
                if answer == 'n':
                    break
                element = input(f"{indent}     Input element (string): ")
                message.metadata_field.append(element)

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### GetModelStatusRequest ###

def gen_GetModelStatusRequest(
        depth: int = 1,
        args: dict = {}
):
    name = 'GetModelStatusRequest'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = get_model_status_pb2.GetModelStatusRequest()

    # model_spec #
    field = 'model_spec'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.model_spec.CopyFrom( gen_ModelSpec(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (ModelSpec) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.model_spec.CopyFrom( gen_ModelSpec(depth + 1) )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### InferenceTask ###

def gen_InferenceTask(
        depth: int = 1,
        args: dict = {}
):
    name = 'InferenceTask'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = inference_pb2.InferenceTask()

    # model_spec #
    field = 'model_spec'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.model_spec.CopyFrom( gen_ModelSpec(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (ModelSpec) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.model_spec.CopyFrom( gen_ModelSpec(depth + 1) )

    # method_name #
    field = 'method_name'
    if field in args:
        print(f"{indent} Setting '{field}' from args: {args[field]}")
        message.method_name = args[field]
    else:
        answer = input(f"{indent} Add '{field}' (string) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.method_name = input(f"{indent}   Input '{field}': ")

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### Input ###

def gen_Input(
        depth: int = 1,
        args: dict = {}
):
    name = 'Input'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = input_pb2.Input()

    # kind #
    field = 'kind'
    if field in args:
        if 'example_list' in args[field]:
            print(f"{indent} Setting 'example_list' from args...")
            message.example_list.CopyFrom( gen_ExampleList(depth + 1, args[field]['example_list']) )
        if 'example_list_with_context' in args[field]:
            print(f"{indent} Setting 'example_list' from args...")
            message.example_list_with_context.CopyFrom( gen_ExampleListWithContext(depth + 1, args[field]['example_list_with_context']) )
    else:
        answer = input(f"{indent} Add '{field}' (oneof) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            oneof_menu = (f"{indent} Available fields:\n"
                          f"{indent}   1.example_list (ExampleList)\n"
                          f"{indent}   2.example_list_with_context (ExampleListWithContext)\n"
                          f"{indent} Choose a field: ")
            answer = int( input(oneof_menu) )
            if answer == 1:
                message.example_list.CopyFrom( gen_ExampleList(depth + 1) )
            if answer == 2:
                message.example_list_with_context.CopyFrom( gen_ExampleListWithContext(depth + 1) )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### LogCollectorConfig ###

def gen_LogCollectorConfig(
        depth: int = 1,
        args: dict = {}
):
    name = 'LogCollectorConfig'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = log_collector_config_pb2.LogCollectorConfig()

    # type #
    field = 'type'
    if field in args:
        print(f"{indent} Setting '{field}' from args: {args[field]}")
        message.type = args[field]
    else:
        answer = input(f"{indent} Add '{field}' (string) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.type = input(f"{indent}   Input '{field}': ")

    # filename_prefix #
    field = 'filename_prefix'
    if field in args:
        print(f"{indent} Setting '{field}' from args: {args[field]}")
        message.filename_prefix = args[field]
    else:
        answer = input(f"{indent} Add '{field}' (string) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.filename_prefix = input(f"{indent}   Input '{field}': ")

    print(f"{indent} No more fields left in '{name}' message.")

    return message


# LoggingConfig #

def gen_LoggingConfig(
        depth: int = 1,
        args: dict = {}
):
    name = 'LoggingConfig'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = logging_config_pb2.LoggingConfig()

    # log_collector_config #
    field = 'log_collector_config'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.log_collector_config.CopyFrom( gen_LogCollectorConfig(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (LogCollectorConfig) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.log_collector_config.CopyFrom( gen_LogCollectorConfig(depth + 1) )

    # sampling_config #
    field = 'sampling_config'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.sampling_config.CopyFrom( gen_SamplingConfig(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (SamplingConfig) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.sampling_config.CopyFrom( gen_SamplingConfig(depth + 1) )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### ModelConfig ###

def gen_ModelConfig(
        depth: int = 1,
        args: dict = {}
):
    name = 'ModelConfig'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = model_server_config_pb2.ModelConfig()

    # name #
    field = 'name'
    if field in args:
        print(f"{indent} Setting '{field}' from args: {args[field]}")
        message.name = args[field]
    else:
        answer = input(f"{indent} Add '{field}' (string) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.name = input(f"{indent}   Input '{field}': ")

    # base_path #
    field = 'base_path'
    if field in args:
        print(f"{indent} Setting '{field}' from args: {args[field]}")
        message.base_path = args[field]
    else:
        answer = input(f"{indent} Add '{field}' (string) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.base_path = input(f"{indent}   Input '{field}': ")

    # model_platform #
    field = 'model_platform'
    if field in args:
        print(f"{indent} Setting '{field}' from args: {args[field]}")
        message.model_platform = args[field]
    else:
        answer = input(f"{indent} Add '{field}' (string) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.model_platform = input(f"{indent}   Input '{field}' (e.g. 'tensorflow'): ")

    # model_version_policy #
    field = 'model_version_policy'
    if field in args:
        print(f"{indent} Setting '{field}' from args: {args[field]}")
        message.model_version_policy.CopyFrom( gen_ServableVersionPolicy(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (ServableVersionPolicy) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.model_version_policy.CopyFrom( gen_ServableVersionPolicy(depth + 1) )

    # version_labels #
    field = 'version_labels'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        for element_key in args[field]:
            element_value = args[field][element_key]
            message.version_labels[element_key] = element_value
    else:
        answer = input(f"{indent} Add '{field}' (map<string, int64>) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            while True:
                answer = input(f"{indent}   Add element to '{field}'? (Yes: any | No 'n'): ")
                if answer == 'n':
                    break

                element_key = input(f"{indent}     Input element key (string): ")
                element_value = int( input(f"{indent}     Input element value (int): ") )
                message.version_labels[element_key] = element_value

    # logging_config #
    field = 'logging_config'
    if field in args:
        print(f"{indent} Setting '{field}' from args: {args[field]}")
        message.logging_config.CopyFrom( gen_LoggingConfig(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (LoggingConfig) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.logging_config.CopyFrom( gen_LoggingConfig(depth + 1) )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### ModelConfigList ###

def gen_ModelConfigList(
        depth: int = 1,
        args: dict = {}
):
    name = 'ModelConfigList'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = model_server_config_pb2.ModelConfigList()

    # config #
    field = 'config'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        for element in args[field]:
            submessage = message.config.add()
            submessage.CopyFrom( gen_ModelConfig(depth + 1, element))
    else:
        answer = input(f"{indent} Add '{field}' (repeated ModelConfig) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            while True:
                answer = input(f"{indent}   Add element to '{field}'? (Yes: any | No 'n'): ")
                if answer == 'n':
                    break

                submessage = message.config.add()
                submessage.CopyFrom( gen_ModelConfig(depth + 1) )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### ModelServerConfig ###

def gen_ModelServerConfig(
        depth: int = 1,
        args: dict = {}
):
    name = 'ModelServerConfig'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = model_server_config_pb2.ModelServerConfig()

    # config #
    field = 'config'
    if field in args:
        if 'model_config_list' in args[field]:
            print(f"{indent} Setting 'model_config_list' from args...")
            message.model_config_list.CopyFrom( gen_ModelConfigList(depth + 1, args[field]['model_config_list']) )
        if 'custom_model_config' in args[field]:
            print(f"{indent} WARNING: 'custom_model_config' unsupported")
    else:
        answer = input(f"{indent} Add '{field}' (oneof) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            oneof_menu = (f"{indent} Available fields:\n"
                          f"{indent}   1.model_config_list (ModelConfigList)\n"
                          f"{indent}   2.[UNSUPPORTED] custom_model_config (google.protobuf.Any)\n"
                          f"{indent} Choose a field: ")
            answer = int( input(oneof_menu) )
            if answer == 1:
                message.model_config_list.CopyFrom( gen_ModelConfigList(depth + 1) )
            if answer == 2:
                print(f"{indent} WARNING: 'custom_model_config' unsupported")

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### ModelSpec ###

def gen_ModelSpec(
        depth: int = 1,
        args: dict = {}
):
    name = 'ModelSpec'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = model_pb2.ModelSpec()

    # name #
    field = 'name'
    if field in args:
        print(f"{indent} Setting '{field}' from args: {args[field]}")
        message.name = args[field]
    else:
        answer = input(f"{indent} Add '{field}' (string) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.name = input(f"{indent}   Input '{field}': ")

    # version_choice #
    field = 'version_choice'
    if field in args:
        if 'version' in args[field]:
            print(f"{indent} Setting 'version' from args: {args[field]['version']}")
            message.version.value = int( args[field]['version'] )
        if 'version_label' in args[field]:
            print(f"{indent} Setting 'version_label' from args: {args[field]['version_label']}")
            message.version_label = int( args[field]['version_label'] )
    else:
        answer = input(f"{indent} Add '{field}' (oneof) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            oneof_menu = (f"{indent} Available fields:\n"
                          f"{indent}   1.version (google.protobufInt64Value)\n"
                          f"{indent}   2.version_label (string)\n"
                          f"{indent} Choose a field: ")
            answer = int( input(oneof_menu) )
            if answer == 1:
                subname = 'google.protobuf.Int64Value'
                print(f"{indent}> Generating '{subname}' message...")
                
                field = 'value'
                answer = input(f"{indent}> Add '{field}' (int) field? (Yes: any | No 'n'): ")
                if answer != 'n':
                    message.version.value = int( input(f"{indent}>   Input '{field}': ") )

                print(f"{indent}> No more fields left in '{subname}' message.")
            if answer == 2:
                field = 'version_label'
                message.version_label = input(f"{indent}   Input '{field}': ")

    # signature_name #
    field = 'signature_name'
    if field in args:
        print(f"{indent} Setting '{field}' from args: {args[field]}")
        message.signature_name = args[field]
    else:
        answer = input(f"{indent} Add '{field}' (string) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.signature_name = input(f"{indent}   Input '{field}': ")

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### MultiInferenceRequest ###

def gen_MultiInferenceRequest(
        depth: int = 1,
        args: dict = {}
):
    name = 'MultiInferenceRequest'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = inference_pb2.MultiInferenceRequest()

    # tasks #
    field = 'tasks'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        for element in args[field]:
            inference_task = message.tasks.add()
            inference_task.CopyFrom( gen_InferenceTask(depth + 1, element))
    else:
        answer = input(f"{indent} Add '{field}' (repeated InferenceTask) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            while True:
                answer = input(f"{indent}   Add element to '{field}'? (Yes: any | No 'n'): ")
                if answer == 'n':
                    break

                element = gen_InferenceTask(depth + 1)
                message.tasks.append(element)

    # input #
    field = 'input'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.input.CopyFrom( gen_Input(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (Input) field? (Yes: any | No 'n'): ")
        message.input.CopyFrom( gen_Input(depth + 1) )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### PredictRequest ###

def gen_PredictRequest(
        depth: int = 1,
        args: dict = {}
):
    name = 'PredictRequest'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = predict_pb2.PredictRequest()

    # model_spec #
    field = 'model_spec'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.model_spec.CopyFrom( gen_ModelSpec(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (ModelSpec) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.model_spec.CopyFrom( gen_ModelSpec(depth + 1) )

    # inputs #
    field = 'inputs'
    if field in args:
        print(f"{indent} Setting '{field}' from args using 'make_tensor_proto'...")
        for key in args[field]:
            tensor_proto = make_tensor_proto(args[field][key])
            message.inputs[key].CopyFrom(tensor_proto)
    else:
        answer = input(f"{indent} Add '{field}' (map<string, TensorProto>) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            while True:
                answer = input(f"{indent}   Add element to '{field}'? (Yes: any | No 'n'): ")
                if answer == 'n':
                    break

                element_key = input(f"{indent}     Input element key (string): ")
                element_value_as_string = input(f"{indent}     Input element value (as list): ")
                element_value_as_list = json.loads(element_value_as_string)
                element_value = make_tensor_proto(element_value_as_list)
                message.inputs[element_key].CopyFrom(element_value)

    # output_filter #
    field = 'output_filter'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.output_filter.extend(args[field])
    else:
        answer = input(f"{indent} Add '{field}' (repeated string) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            while True:
                answer = input(f"{indent}   Add element to '{field}'? (Yes: any | No 'n'): ")
                if answer == 'n':
                    break

                element = input(f"{indent}     Input element (string): ")
                message.output_filter.append(element)

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### RegressionRequest ###

def gen_RegressionRequest(
        depth: int = 1,
        args: dict = {}
):
    name = 'RegressionRequest'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = regression_pb2.RegressionRequest()

    # model_spec #
    field = 'model_spec'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.model_spec.CopyFrom( gen_ModelSpec(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (ModelSpec) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.model_spec.CopyFrom( gen_ModelSpec(depth + 1) )

    # input #
    field = 'input'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.input.CopyFrom( gen_Input(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (Input) field? (Yes: any | No 'n'): ")
        message.input.CopyFrom( gen_Input(depth + 1) )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### ReloadConfigRequest ###

def gen_ReloadConfigRequest(
        depth: int = 1,
        args: dict = {}
):
    name = 'ReloadConfigRequest'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = model_management_pb2.ReloadConfigRequest()

    # config #
    field = 'config'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.config.CopyFrom( gen_ModelServerConfig(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (ModelServerConfig) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.config.CopyFrom( gen_ModelServerConfig(depth + 1) )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### SamplingConfig ###

def gen_SamplingConfig(
        depth: int = 1,
        args: dict = {}
):
    name = 'SamplingConfig'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = logging_config_pb2.SamplingConfig()

    # sampling_rate #
    field = 'sampling_rate'
    if field in args:
        print(f"{indent} Setting '{field}' from args: {args[field]}")
        message.sampling_rate = args[field]
    else:
        answer = input(f"{indent} Add '{field}' (double) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.sampling_rate = float( input(f"{indent}   Input '{field}' (range [0, 1.0]): ") )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


# ServableVersionPolicy #

def gen_ServableVersionPolicy(
        depth: int = 1,
        args: dict = {}
):
    name = 'ServableVersionPolicy'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = file_system_storage_path_source_pb2.FileSystemStoragePathSourceConfig.ServableVersionPolicy()

    # policy_choice #
    field = 'policy_choice'
    if field in args:
        if 'latest' in args[field]:
            print(f"{indent} Setting 'latest' from args...")

            field = 'latest'
            print(f"{indent}> Generating '{field}' (Latest) message...")
            message.latest.SetInParent()

            # num_versions #
            subfield = 'num_versions'
            if subfield in args['policy_choice'][field]:
                print(f"{indent}> Setting '{subfield}' from args: {args['policy_choice'][field][subfield]}")
                message.latest.num_versions = args['policy_choice'][field][subfield]
            else:
                answer = input(f"{indent}> Add '{subfield}' (uint32) field? (Yes: any | No: 'n'): ")
                if answer != 'n':
                    message.latest.num_versions = int( input(f"{indent}>   Input '{subfield}': ") )

            print(f"{indent} No more fields left in '{field}' message.")
        elif 'all' in args[field]:
            print(f"{indent} Setting 'all' from args...")

            field = 'all'
            print(f"{indent}> Generating '{field}' (All) message...")
            message.all.SetInParent()

            print(f"{indent} No more fields left in '{field}' message.")
        elif 'specific' in args[field]:
            print(f"{indent} Setting 'specific' from args...")

            field = 'specific'
            print(f"{indent}> Generating '{field}' (Specific) message...")
            message.specific.SetInParent()

            # versions #
            subfield = 'versions'
            if subfield in args['policy_choice'][field]:
                print(f"{indent}> Setting '{subfield}' from args...")
                message.specific.versions.extend( args['policy_choice'][field][subfield] )
            else:
                answer = input(f"{indent}> Add '{subfield}' (repeated int64) field? (Yes: any | No: 'n'): ")
                if answer != 'n':
                    while True:
                        answer = input(f"{indent}>   Add element to '{subfield}'? (Yes: any | No 'n'): ")
                        if answer == 'n':
                            break

                        element = int( input(f"{indent}>     Input element (int64): ") )
                        message.specific.versions.append(element)

            print(f"{indent} No more fields left in '{field}' message.")
    else:
        answer = input(f"{indent} Add '{field}' (oneof) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            oneof_menu = (f"{indent} Available fields:\n"
                          f"{indent}   1.latest (Latest)\n"
                          f"{indent}   2.all (All)\n"
                          f"{indent}   3.specific (Specific)\n"
                          f"{indent} Choose a field: ")
            answer = int( input(oneof_menu) )
            if answer == 1:
                field = 'latest'
                print(f"{indent}> Generating '{field}' (Latest) message...")
                message.latest.SetInParent()

                # num_versions #
                subfield = 'num_versions'
                answer = input(f"{indent}> Add '{field}' (uint32) field? (Yes: any | No: 'n'): ")
                if answer != 'n':
                    message.latest.num_versions = int( input(f"{indent}>   Input '{subfield}': ") )

                print(f"{indent} No more fields left in '{field}' message.")
            elif answer == 2:
                field = 'all'
                print(f"{indent}> Generating '{field}' (All) message...")
                message.all.SetInParent()

                print(f"{indent} No more fields left in '{field}' message.")
            elif answer == 3:
                field = 'specific'
                print(f"{indent}> Generating '{field}' (Specific) message...")
                message.specific.SetInParent()

                # versions #
                subfield = 'versions'
                answer = input(f"{indent}> Add '{subfield}' (repeated int64) field? (Yes: any | No: 'n'): ")
                if answer != 'n':
                    while True:
                        answer = input(f"{indent}>   Add element to '{subfield}'? (Yes: any | No 'n'): ")
                        if answer == 'n':
                            break

                        element = int( input(f"{indent}>     Input element (int64): ") )
                        message.specific.versions.append(element)

                print(f"{indent} No more fields left in '{field}' message.")

    print(f"{indent} No more fields left in '{name}' message.")

    return message


### mnist:predict_images:PredictRequest ###

def gen_mnist_predict_images_PredictRequest(
        depth: int = 1,
        args: dict = {}
):
    name = 'PredictRequest'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = predict_pb2.PredictRequest()

    if not args:
        args['model_spec'] = {
            'name': 'mnist',
            'signature_name': 'predict_images'
        }

    # model_spec #
    field = 'model_spec'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.model_spec.CopyFrom( gen_ModelSpec(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (ModelSpec) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.model_spec.CopyFrom( gen_ModelSpec(depth + 1) )

    # inputs #
    field = 'inputs'
    if field in args:
        print(f"{indent} Setting '{field}' from args using 'make_tensor_proto'...")
        for key in args[field]:
            tensor_proto = make_tensor_proto(args[field][key])
            message.inputs[key].CopyFrom(tensor_proto)
    else:
        answer = input(f"{indent} Add '{field}' (map<string, TensorProto>) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            print(f"{indent}   Randomly generating Tensor with key 'images' with sample size of 784.")
            samples = int( input(f"{indent}     Input number of samples (int): ") )

            element_key = 'images'
            element_value_as_list = np.random.rand(samples, 28 * 28).tolist()
            element_value = make_tensor_proto(element_value_as_list)
            message.inputs[element_key].CopyFrom(element_value)

    # output_filter #
    field = 'output_filter'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.output_filter.extend(args[field])
    else:
        answer = input(f"{indent} Add '{field}' (repeated string) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            available_outputs = ['scores']
            print(f"{indent}   Available outputs: {available_outputs}")
            while True:
                answer = input(f"{indent}   Add element to '{field}'? (Yes: any | No 'n'): ")
                if answer == 'n':
                    break

                element = input(f"{indent}     Input element (string): ")
                message.output_filter.append(element)

    print(f"{indent} No more fields left in '{name}' message.")

    return message

### mnist:serving_default:ClassificationRequest ###


def gen_mnist_serving_default_ClassificationRequest(
        depth: int = 1,
        args: dict = {}
):
    name = 'ClassificationRequest'
    indent = '>' * depth
    print(f"{indent} Generating '{name}' message...")

    message = classification_pb2.ClassificationRequest()

    if not args:
        args['model_spec'] = {
            'name': 'mnist',
            'signature_name': 'serving_default'
        }

    # model_spec #
    field = 'model_spec'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.model_spec.CopyFrom( gen_ModelSpec(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (ModelSpec) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            message.model_spec.CopyFrom( gen_ModelSpec(depth + 1) )

    # input #
    field = 'input'
    if field in args:
        print(f"{indent} Setting '{field}' from args...")
        message.input.CopyFrom( gen_Input(depth + 1, args[field]) )
    else:
        answer = input(f"{indent} Add '{field}' (Input) field? (Yes: any | No 'n'): ")
        if answer != 'n':
            print(f"{indent}   Randomly generating Input with valid 'mnist' examples.")
            examples = int( input(f"{indent}     Input number of examples (int): ") )

            args['input'] = {
                'kind': {
                    'example_list': {
                        'examples': []
                    }
                }
            }

            for _ in range(examples):
                features = {
                    'x': {
                        'kind': {
                            'float_list': np.random.rand(28 * 28).tolist()
                        }
                    }
                }
                example = {
                    'features': {
                        'feature': features
                    }
                }
                args['input']['kind']['example_list']['examples'].append(example)

            message.input.CopyFrom( gen_Input(depth + 1, args[field]) )

    print(f"{indent} No more fields left in '{name}' message.")

    return message


_MESSAGE_GENERATORS = {
    'ClassificationRequest': gen_ClassificationRequest,
    'Example': gen_Example,
    'ExampleList': gen_ExampleList,
    'ExampleListWithContext': gen_ExampleListWithContext,
    'Feature': gen_Feature,
    'Features': gen_Features,
    'GetModelMetadataRequest': gen_GetModelMetadataRequest,
    'GetModelStatusRequest': gen_GetModelStatusRequest,
    'InferenceTask': gen_InferenceTask,
    'Input': gen_Input,
    'LogCollectorConfig': gen_LogCollectorConfig,
    'LoggingConfig': gen_LoggingConfig,
    'ModelConfig': gen_ModelConfig,
    'ModelConfigList': gen_ModelConfigList,
    'ModelServerConfig': gen_ModelServerConfig,
    'ModelSpec': gen_ModelSpec,
    'MultiInferenceRequest': gen_MultiInferenceRequest,
    'PredictRequest': gen_PredictRequest,
    'RegressionRequest': gen_RegressionRequest,
    'ReloadConfigRequest': gen_ReloadConfigRequest,
    'SamplingConfig': gen_SamplingConfig,
    'ServableVersionPolicy': gen_ServableVersionPolicy,

    'mnist:predict_images:PredictRequest': gen_mnist_predict_images_PredictRequest,
    'mnist:serving_default:ClassificationRequest': gen_mnist_serving_default_ClassificationRequest
}

def get_message_types():
    return list(_MESSAGE_GENERATORS.keys())

def get_message_gen(
        msg_type: str
):
    return _MESSAGE_GENERATORS.get(msg_type)