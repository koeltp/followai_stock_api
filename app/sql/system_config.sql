INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (1, 'qwen_model', '千问模型', 'Qwen 模型基础配置', '2026-03-16 06:34:29', '2026-03-18 06:59:33', 0);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (2, 'qwen_model_name', 'qwen-plus', 'Qwen 模型名称', '2026-03-16 08:47:44', '2026-03-18 06:59:33', 1);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (3, 'qwen_api_key', '请填写你的Qwen API密钥', 'Qwen API 密钥', '2026-03-16 06:34:29', '2026-03-18 06:59:33', 1);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (4, 'qwen_base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1', 'Qwen API 基础URL', '2026-03-16 06:34:29', '2026-03-18 06:59:33', 1);

INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (5, 'qwen_model_price', '千问价格', 'Qwen 模型价格配置', '2026-03-16 07:37:57', '2026-03-18 06:59:33', 0);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (6, 'qwen_input_price', '0.0008', 'Qwen API 输入价格（元/千tokens）', '2026-03-16 07:18:10', '2026-03-18 06:59:33', 5);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (7, 'qwen_output_price', '0.0048', 'Qwen API 输出价格（元/千tokens）', '2026-03-16 07:18:10', '2026-03-18 06:59:33', 5);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (8, 'qwen.standard.input.price', '0.0008', 'Qwen API 标准输入价格（元/千tokens）', '2026-03-16 07:26:44', '2026-03-18 06:59:33', 5);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (9, 'qwen.standard.output.price', '0.0048', 'Qwen API 标准输出价格（元/千tokens）', '2026-03-16 07:26:44', '2026-03-18 06:59:33', 5);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (10, 'qwen.batch.file.input.price', '0.0004', 'Qwen API Batch File 输入价格（元/千tokens）', '2026-03-16 07:26:44', '2026-03-18 06:59:33', 5);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (11, 'qwen.batch.file.output.price', '0.0024', 'Qwen API Batch File 输出价格（元/千tokens）', '2026-03-16 07:26:44', '2026-03-18 06:59:33', 5);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (12, 'qwen.batch.chat.input.price', '0.0004', 'Qwen API Batch Chat 输入价格（元/千tokens）', '2026-03-16 07:26:44', '2026-03-18 06:59:33', 5);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (13, 'qwen.batch.chat.output.price', '0.0024', 'Qwen API Batch Chat 输出价格（元/千tokens）', '2026-03-16 07:26:44', '2026-03-18 06:59:33', 5);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (14, 'qwen.cache.create.price', '0.001', 'Qwen API 显式缓存创建价格（元/千tokens）', '2026-03-16 07:26:44', '2026-03-18 06:59:33', 5);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (15, 'qwen.cache.hit.price', '0.00008', 'Qwen API 显式缓存命中价格（元/千tokens）', '2026-03-16 07:26:44', '2026-03-18 06:59:33', 5);

INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (16, 'longport', '长桥证券配置', 'LongPort 配置', '2026-03-18 03:17:55', '2026-03-18 03:19:52', 0);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (17, 'longport_app_key', '请填写你的longport_app_key', 'LongPort App Key', '2026-03-18 03:11:39', '2026-03-18 03:19:25', 16);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (18, 'longport_app_secret', '请填写你的longport_app_secret', 'LongPort App Secret', '2026-03-18 03:11:39', '2026-03-18 03:19:25', 16);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (19, 'longport_access_token', '请填写你的longport_access_token', 'LongPort Access Token', '2026-03-18 03:11:39', '2026-03-18 03:19:25', 16);
INSERT INTO xszb.system_config (id, key_name, key_value, description, created_at, updated_at, parent) VALUES (20, 'longport_region', 'cn', 'LongPort API 服务器接入点 (hk, cn)', '2026-03-18 03:11:39', '2026-03-18 03:17:55', 16);

