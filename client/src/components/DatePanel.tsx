import { useCallback, useEffect, useMemo, useState } from 'react';
import Alert from 'react-bootstrap/Alert';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { useI18n } from '../i18nContext';
import { localToday, monthRange, weekRange, yearRange } from '../dates';
import type { DateRange } from '../dates';
import { ItemDisplay } from './ItemDisplay';
import { BulkBar } from './BulkBar';
import { useSelection } from './useSelection';
import type { TodoItem } from './ItemDisplay';

interface Briefing {
    summary: string;
    focus: { item_id: string; name: string; reason: string }[];
    warnings: string[];
    tips: string[];
}

const NO_ITEMS: TodoItem[] = [];

type RangeMode = 'today' | 'week' | 'month' | 'year' | 'calendar';
const MODES: RangeMode[] = ['today', 'week', 'month', 'year', 'calendar'];

/**
 * 날자별 검색 (검색 메뉴의 서브 메뉴): 드롭다운에서 조회 기간을 고르면, 선택한 항목 이름이 제목이 되고 해당 기간의
 * 일정(기한이 있는 항목)을 보여준다. 등록(Register) 여부와 무관하다.
 *  - 오늘 일정: 오늘 + 기한이 지났지만 아직 완료하지 않은 항목
 *  - 주간(이번 주, 월~일) / 월간(이번 달) / 연간(올해): 그 기간 안의 항목
 *  - 캘린더: 직접 고른 시작일~종료일(양끝 포함) 안의 항목
 */
export function DatePanel() {
    const { t } = useI18n();
    // 화면에 머무는 동안 날짜가 바뀌지 않도록 마운트 시점의 로컬 오늘을 사용
    const today = useMemo(() => localToday(), []);
    const [mode, setMode] = useState<RangeMode>('today');
    const [calStart, setCalStart] = useState(today);
    const [calEnd, setCalEnd] = useState(today);
    const [items, setItems] = useState<TodoItem[] | null>(null);
    const [aiEnabled, setAiEnabled] = useState(false);
    const [briefing, setBriefing] = useState<Briefing | null>(null);
    const [briefingState, setBriefingState] = useState<
        'idle' | 'loading' | 'failed'
    >('idle');
    const selection = useSelection(items ?? NO_ITEMS);
    const clearSelection = selection.clear;

    useEffect(() => {
        fetch('/api/ai/status')
            .then((r) => (r.ok ? r.json() : { enabled: false }))
            .then((data: { enabled?: boolean }) =>
                setAiEnabled(Boolean(data.enabled)),
            )
            .catch(() => setAiEnabled(false));
    }, []);

    // AI 브리핑: OpenAI 에이전트가 서버에서 할 일 DB 를 직접 조회해 오늘의 우선순위를 알려준다
    const loadBriefing = () => {
        setBriefingState('loading');
        fetch('/api/ai/briefing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ today }),
        })
            .then((r) => {
                if (!r.ok) throw new Error(`HTTP error ${r.status}`);
                return r.json() as Promise<Briefing>;
            })
            .then((data) => {
                setBriefing(data);
                setBriefingState('idle');
            })
            .catch((err: unknown) => {
                console.error('Failed to load briefing:', err);
                setBriefingState('failed');
            });
    };

    const range: DateRange = useMemo(() => {
        switch (mode) {
            case 'week':
                return weekRange(today);
            case 'month':
                return monthRange(today);
            case 'year':
                return yearRange(today);
            case 'calendar':
                return [calStart, calEnd];
            default:
                return [today, today];
        }
    }, [mode, today, calStart, calEnd]);
    const [rangeStart, rangeEnd] = range;

    // 캘린더: 두 날짜가 모두 있고 시작일 ≤ 종료일일 때만 조회할 수 있다
    const missingDate = mode === 'calendar' && (!calStart || !calEnd);
    const reversed = mode === 'calendar' && !missingDate && calStart > calEnd;
    const invalid = missingDate || reversed;

    useEffect(() => {
        clearSelection();
        if (invalid) {
            setItems([]);
            return;
        }
        const controller = new AbortController();
        setItems(null);
        const url =
            mode === 'today'
                ? `/api/schedule?date=${today}`
                : `/api/schedule?start=${rangeStart}&end=${rangeEnd}`;
        fetch(url, { signal: controller.signal })
            .then((r) => {
                if (!r.ok) throw new Error(`HTTP error ${r.status}`);
                return r.json() as Promise<TodoItem[]>;
            })
            .then((data) => setItems(Array.isArray(data) ? data : []))
            .catch((err: unknown) => {
                if (err instanceof DOMException && err.name === 'AbortError')
                    return;
                console.error('Failed to load schedule:', err);
                setItems([]);
            });
        return () => controller.abort();
    }, [mode, today, rangeStart, rangeEnd, invalid, clearSelection]);

    // 수정 후에도 현재 조회 조건에 맞으면 남기고 아니면 목록에서 뺀다
    const stillListed = useCallback(
        (item: TodoItem) => {
            const due = item.due_date;
            if (!due) return false;
            if (mode === 'today') {
                return due === today || (due < today && !item.completed);
            }
            return due >= rangeStart && due <= rangeEnd;
        },
        [mode, today, rangeStart, rangeEnd],
    );

    const onItemUpdate = useCallback(
        (item: TodoItem) => {
            setItems((prev) =>
                (prev ?? [])
                    .map((i) => (i.id === item.id ? item : i))
                    .filter(stillListed),
            );
        },
        [stillListed],
    );

    const renderList = (list: TodoItem[]) =>
        list.map((item) => (
            <ItemDisplay
                key={item.id}
                item={item}
                aiEnabled={aiEnabled}
                hideRegister
                onItemUpdate={onItemUpdate}
                selected={selection.isSelected(item.id)}
                onSelectChange={(checked) => selection.setOne(item.id, checked)}
            />
        ));

    const list = items ?? NO_ITEMS;
    const overdue =
        mode === 'today' ? list.filter((i) => (i.due_date ?? '') < today) : [];
    const todays =
        mode === 'today' ? list.filter((i) => i.due_date === today) : list;

    const periodText =
        rangeStart === rangeEnd ? rangeStart : `${rangeStart} ~ ${rangeEnd}`;

    return (
        <>
            <Form.Select
                className="mb-3"
                aria-label={t('rangeSelectLabel')}
                value={mode}
                onChange={(e) => setMode(e.target.value as RangeMode)}
            >
                {MODES.map((m) => (
                    <option key={m} value={m}>
                        {t(`range.${m}`)}
                    </option>
                ))}
            </Form.Select>

            {aiEnabled && (
                <div className="mb-3">
                    <Button
                        variant="outline-secondary"
                        size="sm"
                        onClick={loadBriefing}
                        disabled={briefingState === 'loading'}
                    >
                        {briefingState === 'loading'
                            ? t('briefingLoading')
                            : t('briefingBtn')}
                    </Button>
                    {briefingState === 'failed' && (
                        <p className="text-danger small mt-2 mb-0">
                            {t('briefingFailed')}
                        </p>
                    )}
                    {briefing && (
                        <Alert variant="light" className="mt-2 mb-0">
                            <p className="mb-2">{briefing.summary}</p>
                            {briefing.focus.length > 0 && (
                                <>
                                    <strong>{t('briefingFocus')}</strong>
                                    <ol className="mb-2">
                                        {briefing.focus.map((f) => (
                                            <li key={f.item_id}>
                                                {f.name}
                                                <span className="text-muted">
                                                    {' — '}
                                                    {f.reason}
                                                </span>
                                            </li>
                                        ))}
                                    </ol>
                                </>
                            )}
                            {briefing.warnings.length > 0 && (
                                <>
                                    <strong className="text-danger">
                                        {t('briefingWarnings')}
                                    </strong>
                                    <ul className="mb-2">
                                        {briefing.warnings.map((w) => (
                                            <li key={w}>{w}</li>
                                        ))}
                                    </ul>
                                </>
                            )}
                            {briefing.tips.length > 0 && (
                                <>
                                    <strong>{t('briefingTips')}</strong>
                                    <ul className="mb-0">
                                        {briefing.tips.map((tip) => (
                                            <li key={tip}>{tip}</li>
                                        ))}
                                    </ul>
                                </>
                            )}
                        </Alert>
                    )}
                </div>
            )}

            {mode === 'calendar' && (
                <div className="calendar-range mb-3">
                    <Form.Control
                        type="date"
                        aria-label={t('rangeStart')}
                        value={calStart}
                        max={calEnd || undefined}
                        onChange={(e) => setCalStart(e.target.value)}
                    />
                    <span>~</span>
                    <Form.Control
                        type="date"
                        aria-label={t('rangeEnd')}
                        value={calEnd}
                        min={calStart || undefined}
                        onChange={(e) => setCalEnd(e.target.value)}
                    />
                </div>
            )}

            {/* 선택한 드롭다운 항목이 곧 제목 */}
            <h5 className="text-center mb-1">{t(`range.${mode}`)}</h5>
            {!invalid && (
                <p className="text-center text-muted small mb-3">
                    {periodText}
                </p>
            )}

            {reversed && (
                <p className="text-center text-danger">{t('invalidRange')}</p>
            )}
            {missingDate && (
                <p className="text-center text-muted">{t('pickBothDates')}</p>
            )}

            {!invalid && items === null && (
                <p className="text-center">{t('loading')}</p>
            )}
            {!invalid && items !== null && items.length === 0 && (
                <p className="text-center text-muted">{t('noSchedule')}</p>
            )}
            {!invalid && items !== null && items.length > 0 && (
                <p className="text-muted small">
                    {t('resultCount', { n: items.length })}
                </p>
            )}

            {!invalid && items !== null && (
                <>
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
                    {overdue.length > 0 && (
                        <>
                            <h6 className="section-title text-danger">
                                {t('sectionOverdue')} ({overdue.length})
                            </h6>
                            {renderList(overdue)}
                        </>
                    )}
                    {todays.length > 0 && (
                        <>
                            {mode === 'today' && (
                                <h6 className="section-title text-success">
                                    {t('sectionToday')} ({todays.length})
                                </h6>
                            )}
                            {renderList(todays)}
                        </>
                    )}
                </>
            )}
            <p className="text-center text-muted small mt-4">
                {t('scheduleHint')}
            </p>
        </>
    );
}
