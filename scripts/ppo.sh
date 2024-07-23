#!/usr/bin/env bash
#
# Copyright 2024 PKU-Alignment Team. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================


# Initialize variables
ACTOR_MODEL_NAME_OR_PATH=""
CRITIC_MODEL_NAME_OR_PATH=""
REWARD_MODEL_NAME_OR_PATH=""
TRAIN_DATASETS=""
PTX_DATASETS=""
ACTOR_MODEL_NAME_OR_PATH=""
CRITIC_MODEL_NAME_OR_PATH=""
REWARD_MODEL_NAME_OR_PATH=""
TRAIN_DATASETS=""
PTX_DATASETS=""
OUTPUT_DIR=""

# Source the setup script
source ./setup.sh

# Execute deepspeed command
deepspeed \
  --master_port ${MASTER_PORT} \
  --module align_anything.trainers.text_to_text.ppo \
  --actor_model_name_or_path ${ACTOR_MODEL_NAME_OR_PATH} \
  --reward_model_name_or_path ${REWARD_MODEL_NAME_OR_PATH} \
  --reward_critic_model_name_or_path ${CRITIC_MODEL_NAME_OR_PATH} \
  --train_datasets ${TRAIN_DATASETS} \
  --ptx_datasets ${PTX_DATASETS} \
  --output_dir ${OUTPUT_DIR}
