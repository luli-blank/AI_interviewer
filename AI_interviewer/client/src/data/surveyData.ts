// 定义题目类型接口
export interface SurveyQuestion {
  id: string;          // 唯一标识，用于绑定表单数据
  title: string;       // 题目内容
  options: {           // 选项列表
    label: string;     // 选项显示的文字
    value: string;     // 选项对应的值
  }[];
  required?: boolean;  // 是否必填
}

// 模拟的外部题目数据
export const questionList: SurveyQuestion[] = [
  {
    id: 'q1',
    title: '在团队合作中，您更倾向于扮演什么角色？',
    required: true,
    options: [
      { label: '领导者：负责统筹全局，分配任务', value: 'leader' },
      { label: '执行者：专注完成分配的具体工作', value: 'executor' },
      { label: '协调者：润滑人际关系，化解冲突', value: 'coordinator' },
      { label: '创新者：提供新点子和解题思路', value: 'innovator' }
    ]
  },
  {
    id: 'q2',
    title: '当遇到难以解决的技术难题时，您的第一反应是？',
    required: true,
    options: [
      { label: '立即求助同事或导师', value: 'ask' },
      { label: '独自查阅文档和资料尝试解决', value: 'search' },
      { label: '暂时搁置，先做其他事情', value: 'delay' },
      { label: '试图寻找绕过该问题的替代方案', value: 'bypass' }
    ]
  },
  {
    id: 'q3',
    title: '您更喜欢哪种工作环境？',
    required: true,
    options: [
      { label: '安静独立，互不打扰', value: 'quiet' },
      { label: '开放式办公，随时交流', value: 'open' },
      { label: '严格规范，层级分明', value: 'strict' }
    ]
  },
  // 你可以在这里无限添加题目...
];