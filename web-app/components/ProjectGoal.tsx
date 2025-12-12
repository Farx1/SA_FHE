'use client';

export default function ProjectGoal() {
  return (
    <section id="goal" className="py-20 px-4 bg-black border-t border-gray-900">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Project Goal & Showcase
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Demonstrating privacy-preserving machine learning with Fully Homomorphic Encryption
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 mb-12">
          {/* Main Goal */}
          <div className="bg-gradient-to-br from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-xl p-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-orange-500 rounded-lg flex items-center justify-center text-3xl">
                🎯
              </div>
              <h3 className="text-2xl font-bold text-white">Project Goal</h3>
            </div>
            <p className="text-gray-300 leading-relaxed mb-4">
              This project demonstrates how to perform <span className="text-red-300 font-semibold">sentiment analysis</span> on encrypted data using 
              Fully Homomorphic Encryption (FHE). The goal is to showcase that machine learning can be performed 
              <span className="text-orange-300 font-semibold"> without ever decrypting the data</span>.
            </p>
            <p className="text-gray-300 leading-relaxed">
              This is a complete, production-ready demonstration of privacy-preserving AI that can be used for 
              sensitive applications where data confidentiality is critical.
            </p>
          </div>

          {/* Key Achievements */}
          <div className="bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/20 rounded-xl p-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center text-3xl">
                ✨
              </div>
              <h3 className="text-2xl font-bold text-white">Key Achievements</h3>
            </div>
            <ul className="space-y-3 text-gray-300">
              <li className="flex items-start gap-3">
                <span className="text-red-400 mt-1">✓</span>
                <span><strong>89% Accuracy:</strong> High-performance model trained on 2000 examples</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-red-400 mt-1">✓</span>
                <span><strong>Complete FHE Pipeline:</strong> All 5 steps implemented and visualized</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-red-400 mt-1">✓</span>
                <span><strong>Windows Compatible:</strong> Works natively with FHE simulator</span>
              </li>
              <li className="flex items-start gap-3">
                <span className="text-red-400 mt-1">✓</span>
                <span><strong>Production Ready:</strong> Full API integration and modern web interface</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Use Cases */}
        <div className="bg-gray-900 rounded-xl p-8 border border-gray-800">
          <h3 className="text-2xl font-bold text-white mb-6">Real-World Applications</h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-black rounded-lg p-6 border border-gray-800">
              <div className="text-3xl mb-3">🏥</div>
              <h4 className="text-lg font-semibold text-red-300 mb-2">Healthcare</h4>
              <p className="text-gray-300 text-sm">
                Analyze patient feedback while maintaining HIPAA compliance and data privacy
              </p>
            </div>
            <div className="bg-black rounded-lg p-6 border border-gray-800">
              <div className="text-3xl mb-3">💼</div>
              <h4 className="text-lg font-semibold text-orange-300 mb-2">Finance</h4>
              <p className="text-gray-300 text-sm">
                Process customer reviews and feedback without exposing sensitive financial data
              </p>
            </div>
            <div className="bg-black rounded-lg p-6 border border-gray-800">
              <div className="text-3xl mb-3">🔐</div>
              <h4 className="text-lg font-semibold text-red-400 mb-2">Government</h4>
              <p className="text-gray-300 text-sm">
                Analyze public sentiment on policies while protecting citizen privacy
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

