'use client';

export default function Footer() {
  return (
    <footer className="py-12 px-4 bg-black border-t border-gray-900">
      <div className="max-w-6xl mx-auto">
        <div className="grid md:grid-cols-3 gap-8 mb-8">
          <div>
            <h3 className="text-xl font-bold text-white mb-4">Sentiment Analysis with FHE</h3>
            <p className="text-gray-400 text-sm">
              Privacy-preserving machine learning using Fully Homomorphic Encryption
            </p>
          </div>
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#goal" className="text-gray-400 hover:text-white transition-colors">Project Goal</a></li>
              <li><a href="#overview" className="text-gray-400 hover:text-white transition-colors">Overview</a></li>
              <li><a href="#dataset" className="text-gray-400 hover:text-white transition-colors">Dataset</a></li>
              <li><a href="#architecture" className="text-gray-400 hover:text-white transition-colors">Architecture</a></li>
              <li><a href="#process" className="text-gray-400 hover:text-white transition-colors">FHE Process</a></li>
              <li><a href="#demo" className="text-gray-400 hover:text-white transition-colors">Demo</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-lg font-semibold text-white mb-4">Technology</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li>RoBERTa Transformer</li>
              <li>XGBoost Classifier</li>
              <li>Concrete-ML / FHE Simulator</li>
              <li>Next.js + Tailwind CSS</li>
            </ul>
          </div>
        </div>
        <div className="pt-8 border-t border-slate-800 text-center text-gray-400 text-sm">
          <p>© 2024 Sentiment Analysis with FHE. Built with Next.js and Tailwind CSS.</p>
        </div>
      </div>
    </footer>
  );
}

