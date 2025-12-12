'use client';

import { ArrowDown } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-red-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-orange-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-red-600 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10 text-center px-4 max-w-5xl mx-auto">
        <div className="mb-8 inline-flex items-center gap-2 px-4 py-2 rounded-full bg-red-500/10 border border-red-500/20 text-red-300 text-sm">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
          </span>
          Fully Homomorphic Encryption
        </div>
        
        <h1 className="text-6xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-white via-red-200 to-orange-200 bg-clip-text text-transparent">
          Sentiment Analysis
          <br />
          <span className="text-5xl md:text-7xl">with FHE</span>
        </h1>
        
        <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
          Analyze sentiment while keeping your data <span className="text-red-300 font-semibold">encrypted</span> throughout the entire processing pipeline.
          <br />
          <span className="text-lg text-gray-400 mt-2 block">
            Privacy-first AI that never sees your data in clear text.
          </span>
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <a
            href="#demo"
            className="px-8 py-4 bg-gradient-to-r from-red-600 to-orange-600 rounded-lg font-semibold text-white hover:from-red-500 hover:to-orange-500 transition-all duration-300 transform hover:scale-105 shadow-lg shadow-red-500/50"
            suppressHydrationWarning
          >
            Try Demo
          </a>
          <a
            href="#goal"
            className="px-8 py-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg font-semibold text-white hover:bg-white/20 transition-all duration-300"
            suppressHydrationWarning
          >
            Learn More
          </a>
        </div>

        <div className="mt-16 animate-bounce">
          <a href="#overview" className="flex flex-col items-center text-gray-400 hover:text-white transition-colors">
            <span className="text-sm mb-2">Scroll to explore</span>
            <ArrowDown className="w-6 h-6" />
          </a>
        </div>
      </div>
    </section>
  );
}

