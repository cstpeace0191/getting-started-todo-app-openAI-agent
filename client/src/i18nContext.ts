import { createContext, useContext } from 'react';

export type Lang = 'ko' | 'en';

const ko = {
    // 공통
    loading: '불러오는 중...',
    delete: '삭제',
    confirm: '확인',
    register: '등록',
    statusDone: '완료(completed)',
    statusTodo: '해야됨(todo)',
    statusTitle: '눌러서 완료/해야됨 전환',
    registerTitle:
        '등록하면 작업 목록에서 사라지고 검색에서 조회할 수 있습니다',
    confirmTitle: '이 항목을 화면에서 숨깁니다 (DB는 유지)',
    deleteTitle: 'DB에서 완전히 삭제합니다',
    deleteConfirm: '이 항목을 DB에서 삭제할까요?',
    // 탭
    tabWork: '작업 목록',
    tabSearch: '검색',
    // 입력 폼
    newItemPlaceholder: '새 할 일',
    addItem: '추가',
    adding: '추가 중...',
    aiClassifyingAdd: 'AI 분류 중...',
    noPending: '등록 대기 중인 항목이 없습니다. 위에서 추가해 보세요!',
    // 분류
    aiClassify: 'AI 분류',
    reclassify: '다시 분류',
    reclassifyTitle: 'AI로 다시 분류',
    classifying: '분류 중...',
    priorityPrefix: '우선순위',
    'category.study': '학업',
    'category.work': '업무',
    'category.personal': '개인',
    'priority.high': '높음',
    'priority.medium': '보통',
    'priority.low': '낮음',
    // 검색
    modeAll: '전체 보기',
    modeCategory: '분류별 검색',
    modeKeyword: '키워드 검색',
    keywordPlaceholder: '키워드로 검색',
    categoryKeywordPlaceholder: '선택한 분류 안에서 검색 (선택)',
    clearSearch: '검색어 지우기',
    pickCategory: '분류를 선택하세요.',
    noCategories: '등록된 분류가 없습니다.',
    enterKeyword: '검색할 키워드를 입력하세요.',
    noResults: '검색 결과가 없습니다.',
    noResultsFor: '"{q}" 검색 결과가 없습니다.',
    resultCount: '총 {n}건',
    registeredOnly: '등록(Register)된 항목만 검색됩니다.',
    // 언어
    language: '언어',
    // 오늘 일정 / 일정 지정
    tabDateSearch: '날자별 검색',
    subSearchRegistered: '등록 항목 검색',
    'range.today': '오늘 일정',
    'range.week': '주간 일정',
    'range.month': '월간 일정',
    'range.year': '연간 일정',
    'range.calendar': '캘린더 검색',
    rangeSelectLabel: '조회 기간',
    rangeStart: '시작일',
    rangeEnd: '종료일',
    invalidRange: '종료일은 시작일보다 빠를 수 없습니다.',
    pickBothDates: '시작일과 종료일을 선택하세요.',
    sectionOverdue: '기한 지남',
    sectionToday: '오늘',
    noSchedule: '해당 기간에 일정이 없습니다.',
    scheduleHint:
        '날짜가 있는 항목만 표시됩니다. 항목을 추가하면 AI가 "내일 오전 9시" 같은 표현에서 날짜를 채우고, 직접 지정할 수도 있습니다.',
    briefingBtn: 'AI 브리핑',
    briefingLoading: 'AI가 일정을 살펴보는 중…',
    briefingFailed: 'AI 브리핑을 만들지 못했습니다.',
    briefingFocus: '오늘 먼저 할 일',
    briefingWarnings: '주의',
    briefingTips: '조언',
    dueOptional: '일정 (선택)',
    dueDate: '날짜',
    dueTime: '시간 (선택)',
    setDue: '날짜 지정',
    editDueTitle: '일정 수정',
    overdueBadge: '지남',
    save: '저장',
    editDone: '수정완료',
    cancel: '취소',
    clearDue: '일정 삭제',
    edit: '수정',
    editTitle: '내용과 일정을 수정합니다',
    editNameLabel: '할 일 내용',
    saving: '저장 중...',
    selectAll: '전체 선택',
    selectItem: '항목 선택',
    deleteSelected: '선택 삭제',
    bulkDeleteConfirm: '선택한 {n}개 항목을 DB에서 삭제할까요?',
} as const;

export type MessageKey = keyof typeof ko;

const en: Record<MessageKey, string> = {
    loading: 'Loading...',
    delete: 'Delete',
    confirm: 'Confirm',
    register: 'Register',
    statusDone: 'Completed',
    statusTodo: 'Todo',
    statusTitle: 'Click to toggle completed / todo',
    registerTitle:
        'Registering removes it from the work list and makes it searchable',
    confirmTitle: 'Hide this item from the screen (kept in the DB)',
    deleteTitle: 'Delete permanently from the DB',
    deleteConfirm: 'Delete this item from the database?',
    tabWork: 'Work list',
    tabSearch: 'Search',
    newItemPlaceholder: 'New Item',
    addItem: 'Add Item',
    adding: 'Adding...',
    aiClassifyingAdd: 'Classifying with AI...',
    noPending: 'No pending items! Add one above!',
    aiClassify: 'AI classify',
    reclassify: 'Reclassify',
    reclassifyTitle: 'Reclassify with AI',
    classifying: 'Classifying...',
    priorityPrefix: 'Priority',
    'category.study': 'Study',
    'category.work': 'Work',
    'category.personal': 'Personal',
    'priority.high': 'High',
    'priority.medium': 'Medium',
    'priority.low': 'Low',
    modeAll: 'Show all',
    modeCategory: 'By category',
    modeKeyword: 'By keyword',
    keywordPlaceholder: 'Search by keyword',
    categoryKeywordPlaceholder: 'Search within selected category (optional)',
    clearSearch: 'Clear search',
    pickCategory: 'Select a category.',
    noCategories: 'No categories yet.',
    enterKeyword: 'Enter a keyword to search.',
    noResults: 'No results found.',
    noResultsFor: 'No results for "{q}".',
    resultCount: '{n} item(s)',
    registeredOnly: 'Only registered items are searched.',
    language: 'Language',
    tabDateSearch: 'Search by date',
    subSearchRegistered: 'Registered items',
    'range.today': "Today's schedule",
    'range.week': 'Weekly schedule',
    'range.month': 'Monthly schedule',
    'range.year': 'Yearly schedule',
    'range.calendar': 'Calendar search',
    rangeSelectLabel: 'Period',
    rangeStart: 'Start date',
    rangeEnd: 'End date',
    invalidRange: 'The end date cannot be earlier than the start date.',
    pickBothDates: 'Select a start date and an end date.',
    sectionOverdue: 'Overdue',
    sectionToday: 'Today',
    noSchedule: 'Nothing scheduled for this period.',
    scheduleHint:
        'Only items with a date are shown. When you add an item, AI fills the date from phrases like "tomorrow 9am"; you can also set it yourself.',
    briefingBtn: 'AI briefing',
    briefingLoading: 'AI is reviewing your schedule…',
    briefingFailed: 'Could not create the AI briefing.',
    briefingFocus: 'Focus first',
    briefingWarnings: 'Heads up',
    briefingTips: 'Tips',
    dueOptional: 'Schedule (optional)',
    dueDate: 'Date',
    dueTime: 'Time (optional)',
    setDue: 'Set date',
    editDueTitle: 'Edit schedule',
    overdueBadge: 'overdue',
    save: 'Save',
    editDone: 'Done',
    cancel: 'Cancel',
    clearDue: 'Remove schedule',
    edit: 'Edit',
    editTitle: 'Edit the content and schedule',
    editNameLabel: 'Item content',
    saving: 'Saving...',
    selectAll: 'Select all',
    selectItem: 'Select item',
    deleteSelected: 'Delete selected',
    bulkDeleteConfirm: 'Delete the {n} selected item(s) from the database?',
};

const MESSAGES: Record<Lang, Record<MessageKey, string>> = { ko, en };

const STORAGE_KEY = 'todo-lang';

export const STORAGE_KEY_LANG = STORAGE_KEY;

export function initialLang(): Lang {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved === 'ko' || saved === 'en') return saved;
    } catch {
        // localStorage 사용 불가 환경은 무시
    }
    return navigator.language?.toLowerCase().startsWith('ko') ? 'ko' : 'en';
}

export function translate(
    lang: Lang,
    key: MessageKey,
    params?: Record<string, string | number>,
): string {
    let text = MESSAGES[lang][key];
    if (params) {
        for (const [name, value] of Object.entries(params)) {
            text = text.replace(`{${name}}`, String(value));
        }
    }
    return text;
}

export interface I18nValue {
    lang: Lang;
    setLang: (lang: Lang) => void;
    t: (key: MessageKey, params?: Record<string, string | number>) => string;
}

export const I18nContext = createContext<I18nValue | null>(null);

export function useI18n(): I18nValue {
    const ctx = useContext(I18nContext);
    if (!ctx) throw new Error('useI18n must be used inside I18nProvider');
    return ctx;
}
