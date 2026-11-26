import { useCallback, useEffect, useState } from 'react';
import { AddItemForm } from './AddNewItemForm';
import { ItemDisplay } from './ItemDisplay';
import type { TodoItem } from './ItemDisplay';
import { useI18n } from '../i18nContext';
import { BulkBar } from './BulkBar';
import { useSelection } from './useSelection';

const NO_ITEMS: TodoItem[] = [];

/** 작업 목록: 모든 항목을 표시한다. 등록(Register) 전에는 '등록' 버튼만, 등록 후에는 완료 토글/수정 버튼이 보인다 */
export function TodoListCard() {
    const { t } = useI18n();
    const [items, setItems] = useState<TodoItem[] | null>(null);
    const [aiEnabled, setAiEnabled] = useState(false);
    const selection = useSelection(items ?? NO_ITEMS);

    // 서버에 OpenAI API 키(OPENAI_API_KEY)가 설정되어 있는지 확인 (AI 분류 버튼 표시 여부)
    useEffect(() => {
        fetch('/api/ai/status')
            .then((r) => (r.ok ? r.json() : { enabled: false }))
            .then((data: { enabled?: boolean }) =>
                setAiEnabled(Boolean(data.enabled)),
            )
            .catch(() => setAiEnabled(false));
    }, []);

    useEffect(() => {
        fetch('/api/items')
            .then((r) => {
                if (!r.ok) throw new Error(`HTTP error ${r.status}`);
                return r.json() as Promise<TodoItem[]>;
            })
            .then((data) => setItems(Array.isArray(data) ? data : []))
            .catch((err: unknown) => {
                console.error('Failed to load items:', err);
                setItems([]);
            });
    }, []);

    const onNewItem = useCallback((newItem: TodoItem) => {
        setItems((prev) => [...(prev ?? []), newItem]);
    }, []);

    const onItemUpdate = useCallback((item: TodoItem) => {
        setItems((prev) => {
            const list = prev ?? [];
            const index = list.findIndex((i) => i.id === item.id);
            if (index === -1) return list;
            return [...list.slice(0, index), item, ...list.slice(index + 1)];
        });
    }, []);

    if (items === null) return t('loading');

    return (
        <>
            <AddItemForm onNewItem={onNewItem} aiEnabled={aiEnabled} />
            {items.length === 0 && (
                <p className="text-center">{t('noPending')}</p>
            )}
            <BulkBar
                total={items.length}
                selectedIds={selection.selectedIds}
                allSelected={selection.allSelected}
                onSelectAll={selection.setAll}
                onDeleted={(ids) =>
                    setItems((prev) =>
                        (prev ?? []).filter((i) => !ids.includes(i.id)),
                    )
                }
            />
            {items.map((item) => (
                <ItemDisplay
                    key={item.id}
                    item={item}
                    aiEnabled={aiEnabled}
                    onItemUpdate={onItemUpdate}
                    selected={selection.isSelected(item.id)}
                    onSelectChange={(checked) =>
                        selection.setOne(item.id, checked)
                    }
                />
            ))}
        </>
    );
}
