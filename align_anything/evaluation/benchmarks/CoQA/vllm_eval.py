import os

import argparse
from align_anything.evaluation.eval.base_eval import BaseEval_vllm
from align_anything.evaluation.inference.base_inference import BaseInferencer_vllm
from align_anything.evaluation.dataloader.base_dataloader import BaseDataLoader
from typing import Union, List, Dict, Any, Tuple
from align_anything.utils.tools import read_eval_cfgs, dict_to_namedtuple, update_dict, custom_cfgs_to_dict
from align_anything.utils.template_registry import get_template_class
from align_anything.evaluation.data_type import InferenceInput, InferenceOutput
from align_anything.evaluation.inference.base_inference import update_results
from datasets import Dataset
import json

class CoQADataLoader(BaseDataLoader):

    def get_task_names(self):
        if isinstance(self.data_cfgs.task, list):
            return self.data_cfgs.task
        else:
            task_names = [
            self.data_cfgs.task
            ]
            return task_names

    def get_answer(self, data):
        return data['answer']

    def build_example_prompt(self, data, with_answer=True):
        question = "\n".join(data['questions'])
        answer = ".\n".join(data['answers']['input_text'])
        return f"{data['story']}\n{question}\n{answer}"

    def build_prompt(self, data):
        prompt = f"The following are questions (with stories).\n\n"
        template = get_template_class(self.chat_template)
        question = [template.system_prompt + template.user_prompt.format(input=prompt + self.build_example_prompt(item, False)) + template.assistant_prompt.format(output="") for item in data]
  
        return question
    
    def preprocess(self, data):
        prompts = self.build_prompt(data[self.split].select(range(50)))
        token_ids = self.tokenizer(prompts)

        return prompts, token_ids

class CoQAGeneratorVLLM(BaseInferencer_vllm):

    def eval(self, data:Dict[str, List[InferenceInput]], eval_configs) -> Dict[str, List[InferenceOutput]]:
        task2details = {}
        for task, input in data.items():
            task2details[task] = self.generation(input)
        
        output_dir = eval_configs.output_dir
        brief_filename = eval_configs.brief_filename
        model_id = self.model_cfgs.model_id
        detailed_filename = f'{model_id}_detailed'
        brief_filename = f'{model_id}_brief'
        update_results(output_dir, brief_filename, detailed_filename,task2details) #这一步可以考虑能不能移到外面，目前是把里面的raw_output写了一下
        
        return task2details

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    _, unparsed_args = parser.parse_known_args()
    print(unparsed_args)
    keys = [k[2:] for k in unparsed_args[0::2]]
    values = list(unparsed_args[1::2])
    unparsed_args = dict(zip(keys, values))
    dict_configs, infer_configs = read_eval_cfgs('test_coQA')
    for k, v in unparsed_args.items():
        dict_configs = update_dict(dict_configs, custom_cfgs_to_dict(k, v))
        infer_configs = update_dict(infer_configs, custom_cfgs_to_dict(k, v))
    
    dict_configs, infer_configs = dict_to_namedtuple(dict_configs), dict_to_namedtuple(infer_configs)
    model_config = dict_configs.default.model_cfgs
    eval_configs = dict_configs.default.eval_cfgs
    dataloader = CoQADataLoader(dict_configs)
    test_data = dataloader.load_dataset()
    eval_module = CoQAGeneratorVLLM(model_config, infer_configs)
    eval_module.eval(test_data, eval_configs)
    
if __name__ == '__main__':
    main()