import React from 'react';
import { Slide as SlideType } from '../services/api';

interface SlideProps {
  slide: SlideType;
}

const Slide: React.FC<SlideProps> = ({ slide }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl p-12 min-h-[500px] flex flex-col justify-center">
      <div className="mb-8">
        <span className="text-primary-600 dark:text-primary-400 text-sm font-semibold">
          Слайд {slide.id}
        </span>
      </div>
      
      <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-8">
        {slide.title}
      </h1>
      
      <div className="text-xl md:text-2xl text-gray-700 dark:text-gray-300 leading-relaxed text-left">
        {slide.content}
      </div>
    </div>
  );
};

export default Slide;
