'use client';

import { useState } from 'react';
import { Send, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function DemoSection() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Call the API route
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze sentiment');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const exampleTexts = [
    "I love this product! It's amazing!",
    "This is terrible. I'm very disappointed.",
    "It's okay, nothing special.",
    "The best purchase I've ever made!",
    "Waste of money. Don't buy it."
  ];

  return (
    <section id="demo" className="py-20 px-4 bg-black">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Try the Demo
          </h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Experience real-time sentiment analysis directly in your browser
          </p>
        </div>

        <div className="bg-gradient-to-br from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-2xl p-8 backdrop-blur-sm">
          {/* Input Section */}
          <div className="mb-6">
            <label className="block text-white font-semibold mb-2">
              Enter text to analyze
            </label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Example: 'This product is amazing! I love it!'"
              className="w-full bg-gray-900 border border-gray-700 rounded-lg p-4 text-white placeholder-gray-500 focus:outline-none focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 resize-none"
              rows={4}
              suppressHydrationWarning
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                  handleAnalyze();
                }
              }}
            />
            
            {/* Example Texts */}
            <div className="mt-4">
              <p className="text-sm text-gray-400 mb-2">Quick examples:</p>
              <div className="flex flex-wrap gap-2">
                {exampleTexts.map((example, idx) => (
                  <button
                    key={idx}
                    onClick={() => setText(example)}
                    className="px-3 py-1 text-xs bg-gray-800 border border-gray-700 text-gray-300 rounded-full hover:border-orange-500 hover:text-orange-400 transition-colors"
                    suppressHydrationWarning
                  >
                    {example.substring(0, 30)}...
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Analyze Button */}
          <button
            onClick={handleAnalyze}
            disabled={loading || !text.trim()}
            className="w-full px-8 py-4 bg-gradient-to-r from-red-600 to-orange-600 rounded-lg font-semibold text-white hover:from-red-500 hover:to-orange-500 transition-all duration-300 transform hover:scale-105 shadow-lg shadow-red-500/50 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center gap-2"
            suppressHydrationWarning
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Analyze Sentiment
              </>
            )}
          </button>
          <p className="text-xs text-gray-500 mt-2 text-center">Press Ctrl+Enter to analyze</p>

          {/* Error Display */}
          {error && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-red-400 font-semibold mb-1">Error</h4>
                <p className="text-gray-300 text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Result Display */}
          {result && (
            <div className="mt-6 space-y-4 animate-fadeIn">
              <div className="p-6 bg-gray-900 rounded-lg border border-gray-800">
                <div className="flex items-center gap-3 mb-4">
                  <CheckCircle2 className="w-6 h-6 text-green-400" />
                  <h3 className="text-2xl font-bold text-white">Prediction Result</h3>
                </div>
                
                <div className="grid md:grid-cols-2 gap-4 mb-4">
                  <div className="bg-black rounded-lg p-4 border border-gray-800">
                    <p className="text-sm text-gray-400 mb-1">Sentiment</p>
                    <p className={`text-2xl font-bold ${
                      result.sentiment === 'Positive' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {result.sentiment}
                    </p>
                  </div>
                  <div className="bg-black rounded-lg p-4 border border-gray-800">
                    <p className="text-sm text-gray-400 mb-1">Confidence</p>
                    <p className="text-2xl font-bold text-orange-400">
                      {result.confidence.toFixed(1)}%
                    </p>
                  </div>
                </div>

                <div className="bg-black rounded-lg p-4 border border-gray-800">
                  <p className="text-sm text-gray-400 mb-2">Probabilities</p>
                  <div className="space-y-2">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-300">Negative</span>
                        <span className="text-gray-300">{(result.proba_negative * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-800 rounded-full h-2">
                        <div 
                          className="bg-red-500 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${result.proba_negative * 100}%` }}
                        ></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-300">Positive</span>
                        <span className="text-gray-300">{(result.proba_positive * 100).toFixed(1)}%</span>
                      </div>
                      <div className="w-full bg-gray-800 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full transition-all duration-500"
                          style={{ width: `${result.proba_positive * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>

                {result.processing_time && (
                  <p className="text-xs text-gray-500 mt-4">
                    Processing time: {result.processing_time.toFixed(4)}s
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
