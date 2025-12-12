'use client';

export default function ProjectOverview() {
  return (
    <section id="overview" className="py-20 px-4 bg-black">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            About the Project
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            A demonstration of privacy-preserving machine learning using Fully Homomorphic Encryption
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-gradient-to-br from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-xl p-6 backdrop-blur-sm hover:border-red-500/40 transition-all duration-300">
            <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-orange-500 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Privacy First</h3>
            <p className="text-gray-300">
              Your data remains encrypted throughout processing. The server never sees your text in clear form.
            </p>
          </div>

          <div className="bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/20 rounded-xl p-6 backdrop-blur-sm hover:border-orange-500/40 transition-all duration-300">
            <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">State-of-the-Art</h3>
            <p className="text-gray-300">
              Uses RoBERTa for text processing and XGBoost for classification, achieving 89% accuracy.
            </p>
          </div>

          <div className="bg-gradient-to-br from-red-600/10 to-orange-600/10 border border-red-600/20 rounded-xl p-6 backdrop-blur-sm hover:border-red-600/40 transition-all duration-300">
            <div className="w-12 h-12 bg-gradient-to-br from-red-600 to-orange-600 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Real-Time</h3>
            <p className="text-gray-300">
              Process sentiment analysis in real-time with live statistics and interactive visualizations.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

