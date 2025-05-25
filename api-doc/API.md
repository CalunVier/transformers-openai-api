# 模型响应 API（Responses API）

## 创建模型响应（Create a model response）
```http
POST /v1/responses
```

### 请求体参数
**input**
- 类型：字符串或数组
- 必需项
- 用于模型生成响应的文本、图像或文件输入。
- 了解更多：
  * 文本输入和输出
  * 图像输入
  * 文件输入
  * 对话状态
  * 函数调用

显示可能的类型

---

**model**
- 类型：字符串
- 必需项
- 用于生成响应的模型 ID，例如 `gpt-4o` 或 `o3`。OpenAI 提供广泛的模型，具有不同的能力、性能特征和价格。请参考模型指南以浏览和比较可用模型。

---

**background**
- 类型：布尔值或 null
- 可选项
- 默认值为 false
- 是否在后台运行模型响应。了解更多。

---

**include**
- 类型：数组或 null
- 可选项
- 指定要包含在模型响应中的附加输出数据。目前支持的值为：
  * `file_search_call.results`: 包含文件搜索工具调用的搜索结果。
  * `message.input_image.image_url`: 包含输入消息中的图像 URL。
  * `computer_call_output.output.image_url`: 包含计算机调用输出中的图像 URL。
  * `reasoning.encrypted_content`: 包括推理项输出中推理令牌的加密版本。这使得推理项可以在使用无状态的响应 API 时用于多轮对话（例如，当 `store` 参数设置为 `false`，或当一个组织参与零数据保留计划时）。

---

**instructions**
- 类型：字符串或 null
- 可选项
- 将系统（或开发者）消息插入为模型上下文中的第一个项目。
- 与 `previous_response_id` 一起使用时，前一响应中的指令将不会转移到下一个响应。这使得在新响应中更换系统（或开发者）消息变得简单。

---

**max_output_tokens**
- 类型：整数或 null
- 可选项
- 可生成的响应的标记数量的上限，包括可见输出标记和推理标记。

---

**metadata**
- 类型：映射
- 可选项
- 可附加到对象的一组 16 个键值对。这对于以结构化格式存储关于对象的附加信息以及通过 API 或仪表板查询对象非常有用。
- 键是最长可达 64 个字符的字符串。值是最长可达 512 个字符的字符串。

---

**parallel_tool_calls**
- 类型：布尔值或 null
- 可选项
- 默认值为 true
- 是否允许模型并行运行工具调用。

---

**previous_response_id**
- 类型：字符串或 null
- 可选项
- 上一个模型响应的唯一 ID。使用此 ID 创建多轮对话。了解更多关于对话状态的信息。

---

**reasoning**
- 类型：对象或 null
- 可选项
- **仅适用于 o 系列模型**
- 用于推理模型的配置选项。

显示属性

---

**service_tier**
- 类型：字符串或 null
- 可选项
- 默认值为 auto
- 指定用于处理请求的延迟等级。该参数适用于订阅了规模等级服务的客户：
  * 如果设置为 `auto`，并且项目启用了规模等级，系统将利用规模等级积分，直到积分用尽。
  * 如果设置为 `auto`，并且项目未启用规模等级，请求将使用默认服务等级进行处理，具有较低的正常运行时间 SLA 和没有延迟保证。
  * 如果设置为 `default`，请求将使用默认服务等级进行处理，具有较低的正常运行时间 SLA 和没有延迟保证。
  * 如果设置为 `flex`，请求将使用灵活处理服务等级进行处理。了解更多。
  
  当未设置此参数时，默认行为为 `auto`。

当设置此参数时，响应体将包括使用的 `service_tier`。

---

**store**
- 类型：布尔值或 null
- 可选项
- 默认值为 true
- 是否存储生成的模型响应，以便通过 API 后续检索。

---

**stream**
- 类型：布尔值或 null
- 可选项
- 默认值为 false
- 如果设置为 true，生成的模型响应数据将通过服务器发送事件以流式方式传输给客户端。请参见下面的流媒体部分获取更多信息。

---

**temperature**
- 类型：数字或 null
- 可选项
- 默认值为 1
- 选择使用的采样温度，范围在 0 到 2 之间。较高的值如 0.8 会使输出更加随机，而较低的值如 0.2 会使其更加集中和确定。我们一般建议调整此值或 `top_p`，但不要同时调整这两个。

---

**text**
- 类型：对象
- 可选项
- 用于模型文本响应的配置选项。可以是普通文本或结构化 JSON 数据。了解更多：
  * 文本输入和输出
  * 结构化输出

显示属性

---

**tool_choice**
- 类型：字符串或对象
- 可选项
- 模型在生成响应时应如何选择使用的工具（或工具）。请查看 `tools` 参数，了解如何指定模型可以调用哪些工具。

显示可能的类型

---

**tools**
- 类型：数组
- 可选项
- 模型在生成响应时可能调用的工具数组。可以通过设置 `tool_choice` 参数来指定使用哪个工具。
- 您可以提供给模型的工具有两个类别：
  * **内置工具**：由 OpenAI 提供的工具，扩展了模型的能力，例如网页搜索或文件搜索。了解更多关于内置工具的信息。
  * **函数调用（自定义工具）**：由您定义的函数，使模型能够调用您的代码。了解更多关于函数调用的信息。

显示可能的类型

---

**top_p**
- 类型：数字或 null
- 可选项
- 默认值为 1
- 作为温度采样的替代方案，称为核采样，其中模型考虑的结果是具有 top_p 概率质量的标记。所以 0.1 的意思是只有组成前 10% 概率质量的标记被考虑。
- 我们一般建议调整此值或 `temperature`，但不要同时调整这两个。

---

**truncation**
- 类型：字符串或 null
- 可选项
- 默认值为禁用
- 用于模型响应的截断策略。
  * `auto`: 如果此响应及之前的响应的上下文超过模型的上下文窗口大小，模型将通过在对话的中间删除输入项来截断响应，以适应上下文窗口。
  * `disabled`（默认）：如果模型响应将超过模型的上下文窗口大小，请求将以 400 错误失败。

---

**user**
- 类型：字符串
- 可选项
- 为您的最终用户提供稳定标识符。用于通过更好地分类相似请求来提高缓存命中率，并帮助 OpenAI 检测和防止滥用。了解更多。

#### 示例
Text Input:
```shell
curl https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4.1",
    "input": "Tell me a three sentence bedtime story about a unicorn."
  }'
```

### **返回**
返回一个响应对象。

示例：
```json
{
  "id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
  "object": "response",
  "created_at": 1741476542,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4.1-2025-04-14",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1.0,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1.0,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 36,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 87,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 123
  },
  "user": null,
  "metadata": {}
}

```

**示例请求**:
```json
{
  "model": "gpt-4.1",
  "input": "Tell me a three sentence bedtime story about a unicorn.",
  "temperature": 0.7,
  "stream": true,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search_weather",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string"}
          }
        }
      }
    }
  ]
}
```

## 获取模型响应（Get a model response）
```http
GET /v1/responses/{response_id}
```

### 路径参数
**response_id**
- 类型：字符串
- 必需项
- 要检索的响应 ID。

---

### 查询参数
**include**
- 类型：数组
- 可选项
- 要包含在响应中的附加字段。请参见上述响应创建中的 `include` 参数以获取更多信息。

---

### 返回
返回与指定 ID 匹配的响应对象。

## 删除模型响应（Delete a model response）
```http
DELETE /v1/responses/{response_id}
```

### 路径参数
**response_id**
- 类型：字符串
- 必需项
- 要删除的响应 ID。

---

### 返回
返回一条成功消息。

## 取消响应（Cancel a response）
```http
POST /v1/responses/{response_id}/cancel
```

### 路径参数
**response_id**
- 类型：字符串
- 必需项
- 要取消的响应 ID。

---

### 返回
返回一个响应对象。

## 列出输入项（List input items）
```http
GET /v1/responses/{response_id}/input_items
```

### 路径参数
**response_id**
- 类型：字符串
- 必需项
- 要检索输入项的响应 ID。

---

### 查询参数
**after**
- 类型：字符串
- 可选项
- 用于分页的项目 ID，列出该 ID 之后的项。

**before**
- 类型：字符串
- 可选项
- 用于分页的项目 ID，列出该 ID 之前的项。

**include**
- 类型：数组
- 可选项
- 要包含在响应中的附加字段。请参见上述响应创建中的 `include` 参数以获取更多信息。

**limit**
- 类型：整数
- 可选项
- 默认值为 20
- 返回对象的数量限制。限制范围在 1 到 100 之间，默认值为 20。

**order**
- 类型：字符串
- 可选项
- 返回输入项的顺序。默认值为 `desc`。
  * `asc`: 以升序返回输入项。
  * `desc`: 以降序返回输入项。

---

### 返回
返回输入项对象的列表。

## **Response 对象**

### 属性

- **background**
  - 类型：布尔值或 null
  - 是否在后台运行模型响应。了解更多。

- **created_at**
  - 类型：数字
  - 此响应创建时的 Unix 时间戳（以秒为单位）。

- **error**
  - 类型：对象或 null
  - 当模型无法生成响应时返回的错误对象。

- **id**
  - 类型：字符串
  - 此响应的唯一标识符。

- **incomplete_details**
  - 类型：对象或 null
  - 有关响应不完整的详细信息。

- **instructions**
  - 类型：字符串或 null
  - 将系统（或开发者）消息插入为模型上下文中的第一个项目。
  - 与 `previous_response_id` 一起使用时，前一响应中的指令将不会转移到下一个响应。这使得在新响应中更换系统（或开发者）消息变得简单。

- **max_output_tokens**
  - 类型：整数或 null
  - 可生成响应的标记数量的上限，包括可见输出标记和推理标记。

- **metadata**
  - 类型：映射
  - 可附加到对象的一组 16 个键值对。这对于以结构化格式存储关于对象的附加信息以及通过 API 或仪表板查询对象非常有用。
  - 键是最长可达 64 个字符的字符串。值是最长可达 512 个字符的字符串。

- **model**
  - 类型：字符串
  - 用于生成响应的模型 ID，例如 `gpt-4o` 或 `o3`。OpenAI 提供广泛的模型，具有不同的能力、性能特征和价格。请参考模型指南以浏览和比较可用模型。

- **object**
  - 类型：字符串
  - 此资源的对象类型 - 始终设置为 `response`。

- **output**
  - 类型：数组
  - 模型生成的内容项数组。
  - `output` 数组中的项目长度和顺序取决于模型的响应。
  - 不要仅依赖于访问 `output` 数组中的第一个项目并假设它是模型生成的 `assistant` 消息，可以使用 SDKs 支持的 `output_text` 属性。

- **output_text**
  - 类型：字符串或 null
  - 仅适用于 SDK
  - SDK 专用的便利属性，包含 `output` 数组中所有 `output_text` 项的汇总文本（如果存在）。在 Python 和 JavaScript SDK 中支持。

- **parallel_tool_calls**
  - 类型：布尔值
  - 是否允许模型并行运行工具调用。

- **previous_response_id**
  - 类型：字符串或 null
  - 上一个模型响应的唯一 ID。使用此 ID 创建多轮对话。了解更多关于对话状态的信息。

- **reasoning**
  - 类型：对象或 null
  - **仅适用于 o 系列模型**
  - 用于推理模型的配置选项。
  - 显示属性

- **service_tier**
  - 类型：字符串或 null
  - 指定用于处理请求的延迟等级。该参数适用于订阅了规模等级服务的客户：
    * 设置为 'auto' 且项目启用规模等级，系统将利用规模等级积分，直到积分用尽。
    * 设置为 'auto' 且项目未启用规模等级，请求将使用默认服务等级进行处理，具有较低的正常运行时间 SLA 和没有延迟保证。
    * 设置为 'default'，请求将使用默认服务等级进行处理，具有较低的正常运行时间 SLA 和无延迟保证。
    * 设置为 'flex'，请求将使用灵活处理服务等级进行处理。了解更多。
    * 未设置时，默认为 'auto'。

  设定此参数时，响应体将包括所使用的 `service_tier`。

- **status**
  - 类型：字符串
  - 响应生成的状态。取值之一为 `completed`（完成）、`failed`（失败）、`in_progress`（进行中）、`cancelled`（已取消）、`queued`（队列中）或 `incomplete`（不完整）。

- **temperature**
  - 类型：数字或 null
  - 选择使用的采样温度，范围在 0 到 2 之间。较高的值如 0.8 会使输出更加随机，较低的值如 0.2 会使其更加集中和确定。我们一般建议调整此值或 `top_p`，但不要同时调整这两个。

- **text**
  - 类型：对象
  - 模型文本响应的配置选项。可以是普通文本或结构化的 JSON 数据。了解更多：
    * 文本输入和输出
    * 结构化输出


- **tool_choice**
  - 类型：字符串或对象
  - 模型在生成响应时应如何选择使用的工具（或工具）。请查看 `tools` 参数，了解如何指定模型可以调用哪些工具。
  - 显示可能的类型

- **tools**
  - 类型：数组
  - 模型在生成响应时可能调用的工具数组。可以通过设置 `tool_choice` 参数来指定使用哪个工具。
  - 您可以提供给模型的工具有两个类别：
    * **内置工具**：由 OpenAI 提供的工具，扩展了模型的能力，例如网页搜索或文件搜索。了解更多关于内置工具的信息。
    * **函数调用（自定义工具）**：由您定义的函数，使模型能够调用您的代码。了解更多关于函数调用的信息。

  - 显示可能的类型

- **top_p**
  - 类型：数字或 null
  - 作为温度采样的替代方案，称为核采样，其中模型考虑的结果是具有 top_p 概率质量的标记。所以 0.1 的意思是只有组成前 10% 概率质量的标记被考虑。
  - 我们一般建议调整此值或 `temperature`，但不要同时调整这两个。

- **truncation**
  - 类型：字符串或 null
  - 用于模型响应的截断策略。
    * `auto`: 如果此响应及之前的响应的上下文超过模型的上下文窗口大小，模型将通过在对话的中间删除输入项来截断响应，以适应上下文窗口。
    * `disabled`（默认）：如果模型响应将超过模型的上下文窗口大小，请求将以 400 错误失败。

- **usage**
  - 类型：对象
  - 表示令牌使用详细信息，包括输入令牌、输出令牌、输出令牌的详细分解以及使用的令牌总数。


- **user**
  - 类型：字符串
  - 为您的最终用户提供稳定标识符。用于通过更好地分类相似请求来提高缓存命中率，并帮助 OpenAI 检测和防止滥用。了解更多。

### 示例响应对象（JSON 格式）

```json
{
  "id": "resp_67ccd3a9da748190baa7f1570fe91ac604becb25c45c1d41",
  "object": "response",
  "created_at": 1741476777,
  "status": "completed",
  "error": null,
  "incomplete_details": null,
  "instructions": null,
  "max_output_tokens": null,
  "model": "gpt-4o-2024-08-06",
  "output": [
    {
      "type": "message",
      "id": "msg_67ccd3acc8d48190a77525dc6de64b4104becb25c45c1d41",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "The image depicts a scenic landscape with a wooden boardwalk or pathway leading through lush, green grass under a blue sky with some clouds. The setting suggests a peaceful natural area, possibly a park or nature reserve. There are trees and shrubs in the background.",
          "annotations": []
        }
      ]
    }
  ],
  "parallel_tool_calls": true,
  "previous_response_id": null,
  "reasoning": {
    "effort": null,
    "summary": null
  },
  "store": true,
  "temperature": 1,
  "text": {
    "format": {
      "type": "text"
    }
  },
  "tool_choice": "auto",
  "tools": [],
  "top_p": 1,
  "truncation": "disabled",
  "usage": {
    "input_tokens": 328,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens": 52,
    "output_tokens_details": {
      "reasoning_tokens": 0
    },
    "total_tokens": 380
  },
  "user": null,
  "metadata": {}
}
```


# 聊天补全 API（Chat Completions API）

## 创建聊天补全（Create chat completion）
```http
POST /v1/chat/completions
```

****:
### 请求体参数

**messages**
- 数组，必需
- 包含当前对话的消息列表。根据所使用的模型，不同消息类型（模态）被支持，如文本、图像和音频。

**model**
- 字符串，必需
- 用于生成响应的模型ID，例如 `gpt-4o` 或 `o3`。OpenAI 提供了具有不同能力、性能特征和价格点的广泛模型。请参阅模型指南以浏览和比较可用的模型。

**audio**
- 对象或null，可选
- 用于音频输出的参数。当请求音频输出时需要设置 `modalities: ["audio"]`。

**frequency_penalty**
- 数字或null，可选，默认为0
- 范围在 -2.0 到 2.0 之间。正值会根据新token在文本中的现有频率进行惩罚，减少模型逐字重复相同行的可能性。

**function_call**
- 已弃用
- 字符串或对象，可选
- 已弃用，推荐使用 `tool_choice`。
- 控制模型调用的函数（如果有的话）。

**functions**
- 已弃用
- 数组，可选
- 已弃用，推荐使用 `tools`。
- 模型可能生成JSON输入的函数列表。

**logit_bias**
- 映射，可选，默认为null
- 修改指定token在完成中出现的可能性。

**logprobs**
- 布尔或null，可选，默认为false
- 是否返回输出token的对数概率。

**max_completion_tokens**
- 整数或null，可选
- 限制完成生成的token数量，包括可见输出token和推理token。

**max_tokens**
- 已弃用
- 整数或null，可选
- 聊天完成生成的最大token数量。已弃用，推荐使用 `max_completion_tokens`。

**metadata**
- 映射，可选
- 可附加到对象的一组16个键值对。用于以结构化格式存储附加信息。

**modalities**
- 数组或null，可选
- 您希望模型生成的输出类型。大多数模型默认生成文本。

**n**
- 整数或null，可选，默认为1
- 为每条输入消息生成的聊天完成选择数量。

**parallel_tool_calls**
- 布尔，可选，默认为true
- 是否在工具使用过程中启用并行函数调用。

**prediction**
- 对象，可选
- 预测输出的配置。

**presence_penalty**
- 数字或null，可选，默认为0
- 范围在 -2.0 到 2.0 之间。正值基于token在文本中是否出现进行惩罚。

**reasoning_effort**
- 字符串或null，可选，默认为medium
- 仅限o-series模型。限制推理模型的推理努力。

**response_format**
- 对象，可选
- 指定模型必须输出的格式。

**seed**
- 整数或null，可选
- 此功能处于Beta测试阶段。

**service_tier**
- 字符串或null，可选，默认为auto
- 指定用于处理请求的延迟等级。

**stop**
- 字符串 / 数组 / null，可选，默认为null
- 最新推理模型 `o3` 和 `o4-mini` 不支持。

**store**
- 布尔或null，可选，默认为false
- 是否存储此聊天完成请求的输出。

**stream**
- 布尔或null，可选，默认为false
- 设置为true时，模型响应数据会作为生成时流式传输到客户端。

**stream_options**
- 对象或null，可选，默认为null
- 流响应的选项，仅在您设置 `stream: true` 时设置。

**temperature**
- 数字或null，可选，默认为1
- 使用的采样温度，范围在0到2之间。

**tool_choice**
- 字符串或对象，可选
- 控制模型调用的工具（如果有的话）。

**tools**
- 数组，可选
- 模型可能调用的工具列表。当前，只有函数支持作为工具。

**top_logprobs**
- 整数或null，可选
- 指定每个token位置要返回的最有可能token数量。

**top_p**
- 数字或null，可选，默认为1
- 采样的另一种选择，称为核采样。

**user**
- 字符串，可选
- 您终端用户的稳定标识符。

**web_search_options**
- 对象，可选
- 用于在响应中使用的Web搜索工具。

### **返回值**
返回一个chat completion对象，如果请求是流式的，则返回一系列chat completion chunk对象。

**示例请求**:
```json
{
  "model": "gpt-4.1",
  "messages": [
    {"role": "developer", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the weather today?"}
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string", "description": "City and country"}
          },
          "required": ["location"]
        }
      }
    }
  ],
  "temperature": 0.5,
  "stream": true
}
```

#### 获取聊天补全（Get chat completion）
```http
GET /v1/chat/completions/{completion_id}
```

#### 列出聊天补全（List Chat Completions）
```http
GET /v1/chat/completions
```

**查询参数**:
- **after** (string, 可选): 分页起始ID。
- **limit** (integer, 可选, 默认20): 每页数量。
- **metadata** (map, 可选): 元数据过滤。
- **model** (string, 可选): 模型过滤。
- **order** (string, 可选, 默认asc): 排序顺序。

#### 更新聊天补全（Update chat completion）
```http
POST /v1/chat/completions/{completion_id}
```

**请求体参数**:
- **metadata** (map, 必需): 更新元数据。

#### 删除聊天补全（Delete chat completion）
```http
DELETE /v1/chat/completions/{completion_id}
```


### 音频 API（Audio API）

#### 文本转语音（Create speech）
```http
POST /v1/audio/speech
```

**请求体参数**:
- **input** (string, 必需): 输入文本（最大4096字符）。
- **model** (string, 必需): 语音模型（tts-1/tts-1-hd/gpt-4o-mini-tts）。
- **voice** (string, 必需): 语音类型（alloy/ash/ballad等）。
- **instructions** (string, 可选, 仅gpt-4o-mini-tts支持): 控制语音风格。
- **response_format** (string, 可选, 默认mp3): 输出格式（mp3/opus/aac等）。
- **speed** (number, 可选, 默认1, 仅tts-1/tts-1-hd支持): 语速（0.25-4.0）。

**示例请求**:
```json
{
  "model": "gpt-4o-mini-tts",
  "input": "The quick brown fox jumps over the lazy dog.",
  "voice": "alloy",
  "speed": 1.2
}
```

#### 语音转文本（Create transcription）
```http
POST /v1/audio/transcriptions
```

**请求体参数**:
- **file** (file, 必需): 音频文件（flac/mp3/wav等格式）。
- **model** (string, 必需): 转录模型（gpt-4o-transcribe/whisper-1）。
- **chunking_strategy** ("auto"/object, 可选): 音频分块策略。
- **include[]** (array, 可选): 额外包含的信息（如logprobs）。
- **language** (string, 可选): 输入语言（ISO-639-1格式）。
- **prompt** (string, 可选): 引导转录的提示文本。
- **response_format** (string, 可选, 默认json): 输出格式（json/text/srt等）。
- **stream** (boolean/null, 可选, 默认false): 是否流式响应（仅gpt-4o-transcribe支持）。
- **temperature** (number, 可选, 默认0): 采样温度（0-1）。
- **timestamp_granularities[]** (array, 可选, 默认["segment"]): 时间戳粒度（word/segment）。

#### 音频翻译（Create translation）
```http
POST /v1/audio/translations
```

**请求体参数**:
- **file** (file, 必需): 音频文件。
- **model** (string, 必需, 仅whisper-1支持): 翻译模型。
- **prompt** (string, 可选): 引导翻译的提示文本。
- **response_format** (string, 可选, 默认json): 输出格式。
- **temperature** (number, 可选, 默认0): 采样温度。


### 图像 API（Images API）

#### 创建图像（Create image）
```http
POST /v1/images/generations
```

**请求体参数**:
- **prompt** (string, 必需): 图像描述（gpt-image-1最大32000字符，dall-e-2最大1000字符）。
- **background** (string/null, 可选, 默认auto, gpt-image-1支持): 背景透明度（transparent/opaque/auto）。
- **model** (string, 可选, 默认dall-e-2): 模型（dall-e-2/dall-e-3/gpt-image-1）。
- **moderation** (string/null, 可选, 默认auto, gpt-image-1支持): 内容审核级别（low/auto）。
- **n** (integer/null, 可选, 默认1, dall-e-3仅支持1): 生成数量（1-10）。
- **output_compression** (integer/null, 可选, 默认100, gpt-image-1支持): 输出压缩率（0-100）。
- **output_format** (string/null, 可选, 默认png, gpt-image-1支持): 输出格式（png/jpeg/webp）。
- **quality** (string/null, 可选, 默认auto): 图像质量（auto/high/medium/low，gpt-image-1支持；hd/standard，dall-e-3支持）。
- **response_format** (string/null, 可选, 默认url, dall-e-2/3支持): 响应格式（url/b64_json）。
- **size** (string/null, 可选, 默认auto): 图像尺寸（1024x1024等，不同模型支持不同尺寸）。
- **style** (string/null, 可选, 默认vivid, dall-e-3支持): 图像风格（vivid/natural）。
- **user** (string, 可选): 用户标识符。

**示例请求**:
```json
{
  "model": "gpt-image-1",
  "prompt": "A beautiful sunset over the ocean, with vibrant colors and calm waves",
  "n": 1,
  "size": "1024x1024",
  "output_format": "png"
}
```

#### 编辑图像（Create image edit）
```http
POST /v1/images/edits
```

**请求体参数**:
- **image** (string/array, 必需): 源图像文件或文件列表（gpt-image-1支持最多16张，dall-e-2仅1张）。
- **prompt** (string, 必需): 编辑描述。
- **background** (string/null, 可选, 默认auto, gpt-image-1支持): 背景设置。
- **mask** (file, 可选): 编辑掩码图像（需与源图像同尺寸）。
- **model** (string, 可选, 默认dall-e-2): 模型。
- **n** (integer/null, 可选, 默认1): 生成数量。
- **quality** (string/null, 可选, 默认auto): 质量设置。
- **response_format** (string/null, 可选, 默认url): 响应格式。
- **size** (string/null, 可选, 默认1024x1024): 图像尺寸。
- **user** (string, 可选): 用户标识符。

#### 图像变体（Create image variation）
```http
POST /v1/images/variations
```

**请求体参数**:
- **image** (file, 必需): 源图像文件（PNG，正方形，<4MB）。
- **model** (string, 可选, 默认dall-e-2): 模型。
- **n** (integer/null, 可选, 默认1): 生成数量。
- **response_format** (string/null, 可选, 默认url): 响应格式。
- **size** (string/null, 可选, 默认1024x1024): 图像尺寸。
- **user** (string, 可选): 用户标识符。


### 嵌入 API（Embeddings API）

#### 创建嵌入（Create embeddings）
```http
POST /v1/embeddings
```

**请求体参数**:
- **input** (string/array, 必需): 输入文本或token数组（最大8192 tokens，单次请求总tokens≤300,000）。
- **model** (string, 必需): 嵌入模型（如text-embedding-ada-002）。
- **dimensions** (integer, 可选, 仅text-embedding-3及后续模型支持): 输出维度。
- **encoding_format** (string, 可选, 默认float): 输出格式（float/base64）。
- **user** (string, 可选): 用户标识符。

**示例请求**:
```json
{
  "input": "The food was delicious and the waiter was excellent.",
  "model": "text-embedding-ada-002",
  "encoding_format": "float"
}
```
