import React from 'react';
import AudioPlayer from './AudioPlayer';

interface QAPanelProps {
  question: string;
  answer: string;
  audioBlob: Blob | null;
  isLoading: boolean;
  onClose: () => void;
}

const QAPanel: React.FC<QAPanelProps> = ({ question, answer, audioBlob, isLoading, onClose }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 border-2 border-primary-500">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white">
          Ответ на вопрос
        </h3>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          title="Закрыть"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-12">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-600 mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Обрабатываю ваш вопрос...</p>
        </div>
      ) : (
        <div className="space-y-6">
          {question && (
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <p className="text-sm font-semibold text-blue-900 dark:text-blue-300 mb-2">
                Ваш вопрос:
              </p>
              <p className="text-gray-800 dark:text-gray-200">{question}</p>
            </div>
          )}

          {answer && (
            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <p className="text-sm font-semibold text-green-900 dark:text-green-300 mb-2">
                Ответ:
              </p>
              <p className="text-lg text-gray-800 dark:text-gray-200 leading-relaxed">
                {answer}
              </p>
            </div>
          )}

          {audioBlob && (
            <div>
              <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Прослушать ответ:
              </p>
              <AudioPlayer audioBlob={audioBlob} autoPlay={true} />
            </div>
          )}

          <button
            onClick={onClose}
            className="w-full bg-primary-600 hover:bg-primary-700 text-white py-3 px-6 rounded-lg font-semibold transition-colors"
          >
            Продолжить презентацию
          </button>
        </div>
      )}
    </div>
  );
};

export default QAPanel;
