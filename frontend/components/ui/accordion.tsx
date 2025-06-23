"use client";

import { useState } from "react";

type AccordionProps = {
  question: string;
  answer: React.ReactNode; // Позволяет передавать любой JSX, не только строки
};

export default function Accordion({ question, answer }: AccordionProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border-b border-gray-600 py-4">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex justify-between items-center w-full text-left text-white text-2xl font-semibold focus:outline-none"
      >
        {question}
        <span className="ml-4 text-yellow-400">{isOpen ? "−" : "+"}</span>
      </button>
      {isOpen && (
        <div className="mt-2 text-blue-200 text-xl leading-relaxed">
          {answer}
        </div>
      )}
    </div>
  );
}
