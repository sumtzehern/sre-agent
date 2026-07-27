import type { ReasoningStep } from '../types';
import { useT } from '../i18n';
import styles from './ReasoningChainPanel.module.css';

interface Props {
  steps: ReasoningStep[] | null;
}

const CONFIDENCE_LABEL: Record<ReasoningStep['confidence'], string> = {
  low: '●○○',
  medium: '●●○',
  high: '●●●',
};

export default function ReasoningChainPanel({ steps }: Props) {
  const { t } = useT();

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <span className={styles.dot} />
          <span className={styles.title}>{t('reasoning.title')}</span>
          {steps && (
            <span className={styles.count}>
              {steps.length} {t('reasoning.steps')}
            </span>
          )}
        </div>
      </div>

      <div className={styles.body}>
        {!steps && (
          <div className={styles.empty}>
            {t('reasoning.empty')}
            <br />
            {t('reasoning.emptyHint')}
          </div>
        )}

        {steps?.map((step, i) => (
          <div key={i} className={styles.step}>
            <div className={styles.stepHeader}>
              <span className={styles.stepIndex}>{t('reasoning.step')} {i + 1}</span>
              <span className={`${styles.confidence} ${styles[`confidence_${step.confidence}`]}`}>
                {CONFIDENCE_LABEL[step.confidence]} {step.confidence}
              </span>
            </div>

            <div className={styles.field}>
              <span className={styles.fieldLabel}>{t('reasoning.hypothesis')}</span>
              <p className={styles.fieldValue}>{step.hypothesis}</p>
            </div>

            <div className={styles.field}>
              <span className={styles.fieldLabel}>{t('reasoning.evidence')}</span>
              <div className={styles.evidenceChips}>
                {step.evidenceChecked.map(id => (
                  <span key={id} className={styles.evidenceChip}>{id}</span>
                ))}
              </div>
            </div>

            <div className={styles.field}>
              <span className={styles.fieldLabel}>{t('reasoning.conclusion')}</span>
              <p className={styles.fieldValue}>{step.conclusion}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
