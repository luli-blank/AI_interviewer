# 面试题库嵌入说明

本目录用于存储面试题库的向量嵌入数据。

## 文件说明

- `question_bank.json` - 原始题库数据（JSON 格式）
- `question_embeddings.pkl` - 题库的向量嵌入（Pickle 格式）

## 题库格式

每个题目的 JSON 结构：

```json
{
    "question": "问题内容",
    "reference_answer": "参考答案/评判标准",
    "category": "分类",
    "difficulty": 1-5,
    "tags": ["标签1", "标签2"]
}
```

## 分类说明

- `自我介绍` - 开场和自我介绍类问题
- `项目经验` - 项目经验深挖类问题
- `基础知识-通用` - 通用技术基础
- `基础知识-Python` - Python 相关
- `基础知识-JavaScript` - JavaScript 相关
- `基础知识-Java` - Java 相关
- `场景算法` - 系统设计和算法类
- `反问环节` - 面试结束问题

## 嵌入模型

使用阿里云 DashScope 的 `text-embedding-v3` 模型，维度 1024。

## 自动生成

首次运行时，如果 `question_bank.json` 不存在，系统会自动创建默认题库。
如果 `question_embeddings.pkl` 不存在，系统会自动计算并保存嵌入向量。
