import React from 'react';
import { Slide as SlideType } from '../services/api';
import logo from '../photo_2025-12-23_00-43-53-removebg-preview.png';

interface SlideProps {
  slide: SlideType;
}

const IMAGE_QUERIES: Record<number, string> = {
  1: 'human rights globe',
  2: 'history documents',
  3: 'united nations building',
  4: 'justice scales',
  5: 'democracy voting',
  6: 'workplace equality',
  7: 'healthcare community',
  8: 'education classroom',
  9: 'culture heritage',
  10: 'children protection',
  11: 'women empowerment',
  12: 'disability inclusion',
  13: 'equality rainbow',
  14: 'refugees support',
  15: 'court justice',
  16: 'privacy lock',
  17: 'digital rights cybersecurity',
  18: 'environment nature',
  19: 'business ethics',
  20: 'protest freedom',
  21: 'international law',
  22: 'kyrgyzstan mountains',
  23: 'education training',
  24: 'volunteer community',
  25: 'hope sunrise',
};

const getImageUrl = (slideId: number) => {
  const query = IMAGE_QUERIES[slideId] ?? 'human rights';
  // source.unsplash.com возвращает случайное релевантное фото
  return `https://source.unsplash.com/900x700/?${encodeURIComponent(query)}`;
};

const getSlideImageUrl = (slide: SlideType) => {
  if (slide.image_url && slide.image_url.trim().length > 0) return slide.image_url;
  return getImageUrl(slide.id);
};

const Slide: React.FC<SlideProps> = ({ slide }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-4 md:p-6 relative max-h-[calc(100vh-260px)] overflow-hidden">
      <img
        src={logo}
        alt="Logo"
        className="absolute right-4 top-4 md:right-6 md:top-6 w-12 h-auto md:w-16 select-none"
        draggable={false}
      />

      <div className="pt-10 md:pt-12 h-full overflow-auto pr-1">
        <div className="mb-4 flex items-center justify-between">
          <span className="text-blue-600 dark:text-blue-300 text-sm font-semibold">
            Слайд {slide.id}
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {/* Текст слева */}
        <div className="flex flex-col">
          <h1 className="text-2xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            {slide.title}
          </h1>
          <div className="text-base md:text-lg text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
            {slide.content}
          </div>
        </div>

        {/* Картинка справа */}
        <div className="w-full mt-4 lg:mt-6">
          <div className="rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-900">
            <img
              src={getSlideImageUrl(slide)}
              alt={slide.title}
              className="w-full h-[200px] md:h-[260px] object-cover"
              loading="lazy"
              referrerPolicy="no-referrer"
            />
          </div>
          <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">
            Иллюстрация под тему слайда
          </p>
        </div>
        </div>
      </div>
    </div>
  );
};

export default Slide;
