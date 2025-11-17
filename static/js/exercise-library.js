/**
 * 健身房动作库
 * 按照目标肌肉群分类
 */

const EXERCISE_LIBRARY = {
    chest: {
        name: '胸部',
        icon: '💪',
        color: 'bg-red-50 border-red-200',
        exercises: [
            { name: '杠铃卧推', icon: '🏋️', description: '平板卧推，发展整体胸部力量' },
            { name: '上斜杠铃卧推', icon: '🏋️', description: '上斜板卧推，重点上胸' },
            { name: '下斜杠铃卧推', icon: '🏋️', description: '下斜板卧推，重点下胸' },
            { name: '哑铃卧推', icon: '🏋️', description: '哑铃平板卧推，更大活动范围' },
            { name: '上斜哑铃卧推', icon: '🏋️', description: '上斜哑铃卧推' },
            { name: '哑铃飞鸟', icon: '🦅', description: '平板飞鸟，拉伸胸肌' },
            { name: '龙门架夹胸', icon: '⚙️', description: '绳索夹胸，持续张力' },
            { name: '器械推胸', icon: '🎰', description: '坐姿推胸器械' },
            { name: '双杠臂屈伸', icon: '💪', description: '双杠臂屈伸，下胸杀手' },
        ]
    },
    back: {
        name: '背部',
        icon: '🦾',
        color: 'bg-blue-50 border-blue-200',
        exercises: [
            { name: '引体向上', icon: '🤸', description: '正手引体向上' },
            { name: '反手引体向上', icon: '🤸', description: '反手引体，重点肱二头肌' },
            { name: '高位下拉', icon: '⬇️', description: '坐姿高位下拉' },
            { name: '杠铃划船', icon: '🚣', description: '俯身杠铃划船' },
            { name: '哑铃划船', icon: '🚣', description: '单臂哑铃划船' },
            { name: '坐姿划船', icon: '🚣', description: '器械坐姿划船' },
            { name: '直臂下压', icon: '⬇️', description: '绳索直臂下压' },
            { name: '硬拉', icon: '🏋️', description: '传统硬拉，全身力量' },
            { name: '罗马尼亚硬拉', icon: '🏋️', description: '直腿硬拉' },
        ]
    },
    legs: {
        name: '腿部',
        icon: '🦵',
        color: 'bg-green-50 border-green-200',
        exercises: [
            { name: '深蹲', icon: '🏋️', description: '杠铃深蹲，腿部之王' },
            { name: '前蹲', icon: '🏋️', description: '前置杠铃深蹲' },
            { name: '史密斯深蹲', icon: '🎰', description: '史密斯机深蹲' },
            { name: '腿举', icon: '🦵', description: '45度腿举器械' },
            { name: '腿屈伸', icon: '🦵', description: '坐姿腿屈伸，孤立股四头肌' },
            { name: '腿弯举', icon: '🦵', description: '俯卧腿弯举，股二头肌' },
            { name: '保加利亚分腿蹲', icon: '🦵', description: '单腿蹲，平衡力量' },
            { name: '箭步蹲', icon: '🚶', description: '哑铃箭步蹲' },
            { name: '提踵', icon: '🦶', description: '站姿提踵，小腿' },
        ]
    },
    shoulders: {
        name: '肩部',
        icon: '💪',
        color: 'bg-yellow-50 border-yellow-200',
        exercises: [
            { name: '杠铃推举', icon: '🏋️', description: '站姿杠铃推举' },
            { name: '坐姿杠铃推举', icon: '🏋️', description: '坐姿肩上推举' },
            { name: '哑铃推举', icon: '🏋️', description: '坐姿哑铃推举' },
            { name: '阿诺德推举', icon: '💪', description: '旋转哑铃推举' },
            { name: '侧平举', icon: '🦅', description: '哑铃侧平举，中束' },
            { name: '前平举', icon: '🦅', description: '哑铃前平举，前束' },
            { name: '俯身飞鸟', icon: '🦅', description: '哑铃俯身飞鸟，后束' },
            { name: '直立划船', icon: '🚣', description: '杠铃直立划船' },
            { name: '绳索面拉', icon: '⚙️', description: '绳索面部拉引' },
        ]
    },
    arms: {
        name: '手臂',
        icon: '💪',
        color: 'bg-purple-50 border-purple-200',
        exercises: [
            { name: '杠铃弯举', icon: '🏋️', description: '站姿杠铃弯举' },
            { name: '哑铃弯举', icon: '🏋️', description: '交替哑铃弯举' },
            { name: '锤式弯举', icon: '🔨', description: '哑铃锤式弯举' },
            { name: '集中弯举', icon: '💪', description: '坐姿集中弯举' },
            { name: '牧师凳弯举', icon: '🏋️', description: '斯科特弯举' },
            { name: '窄距卧推', icon: '🏋️', description: '窄距杠铃卧推，三头' },
            { name: '双杠臂屈伸', icon: '💪', description: '三头臂屈伸' },
            { name: '绳索下压', icon: '⬇️', description: '绳索三头下压' },
            { name: '过头臂屈伸', icon: '🏋️', description: '哑铃过头臂屈伸' },
        ]
    },
    core: {
        name: '核心',
        icon: '🎯',
        color: 'bg-orange-50 border-orange-200',
        exercises: [
            { name: '卷腹', icon: '🎯', description: '地面卷腹' },
            { name: '仰卧举腿', icon: '🦵', description: '仰卧抬腿' },
            { name: '悬垂举腿', icon: '🦵', description: '单杠悬垂举腿' },
            { name: '平板支撑', icon: '⏱️', description: '前平板支撑' },
            { name: '侧平板支撑', icon: '⏱️', description: '侧面平板支撑' },
            { name: '俄罗斯转体', icon: '🔄', description: '坐姿转体' },
            { name: '龙旗', icon: '🎌', description: 'Dragon Flag' },
            { name: '腹肌轮', icon: '⚙️', description: '腹轮滚动' },
        ]
    }
};

// 获取所有分类
function getAllCategories() {
    return Object.keys(EXERCISE_LIBRARY).map(key => ({
        key: key,
        ...EXERCISE_LIBRARY[key]
    }));
}

// 根据分类获取动作
function getExercisesByCategory(category) {
    return EXERCISE_LIBRARY[category]?.exercises || [];
}

// 搜索动作
function searchExercises(keyword) {
    const results = [];
    const lowerKeyword = keyword.toLowerCase();

    Object.keys(EXERCISE_LIBRARY).forEach(categoryKey => {
        const category = EXERCISE_LIBRARY[categoryKey];
        const matchedExercises = category.exercises.filter(ex =>
            ex.name.toLowerCase().includes(lowerKeyword) ||
            ex.description.toLowerCase().includes(lowerKeyword)
        );

        if (matchedExercises.length > 0) {
            results.push({
                category: category.name,
                categoryKey: categoryKey,
                exercises: matchedExercises
            });
        }
    });

    return results;
}

// 获取所有动作（扁平化）
function getAllExercises() {
    const allExercises = [];
    Object.keys(EXERCISE_LIBRARY).forEach(categoryKey => {
        const category = EXERCISE_LIBRARY[categoryKey];
        category.exercises.forEach(ex => {
            allExercises.push({
                ...ex,
                category: category.name,
                categoryKey: categoryKey
            });
        });
    });
    return allExercises;
}
