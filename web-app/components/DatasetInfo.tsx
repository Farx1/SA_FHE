'use client';

export default function DatasetInfo() {
  return (
    <section id="dataset" className="py-20 px-4 bg-black">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Dataset & Training
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Learn about the data used to train our sentiment analysis model
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Dataset Information */}
          <div className="bg-gradient-to-br from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-xl p-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-orange-500 rounded-lg flex items-center justify-center text-3xl">
                📊
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">Amazon Polarity Dataset</h3>
                <p className="text-gray-400">Large-scale product reviews</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <h4 className="text-lg font-semibold text-orange-300 mb-2">Dataset Details</h4>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-start gap-2">
                    <span className="text-red-400 mt-1">•</span>
                    <span><strong>Source:</strong> Amazon product reviews</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-red-400 mt-1">•</span>
                    <span><strong>Size:</strong> 2000 examples for training</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-red-400 mt-1">•</span>
                    <span><strong>Split:</strong> 80% training (1600), 20% test (400)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-red-400 mt-1">•</span>
                    <span><strong>Classes:</strong> Negative (0) and Positive (1)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-red-400 mt-1">•</span>
                    <span><strong>Balance:</strong> ~50/50 distribution</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* Training Information */}
          <div className="bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/20 rounded-xl p-8">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center text-3xl">
                🎯
              </div>
              <div>
                <h3 className="text-2xl font-bold text-white">Model Training</h3>
                <p className="text-gray-400">XGBoost with optimized hyperparameters</p>
              </div>
            </div>
            
            <div className="space-y-4">
              <div>
                <h4 className="text-lg font-semibold text-red-300 mb-2">Training Configuration</h4>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-start gap-2">
                    <span className="text-orange-400 mt-1">•</span>
                    <span><strong>Algorithm:</strong> XGBoost Classifier</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-orange-400 mt-1">•</span>
                    <span><strong>Cross-Validation:</strong> 5-fold CV</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-orange-400 mt-1">•</span>
                    <span><strong>Hyperparameters:</strong> Grid search optimization</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-orange-400 mt-1">•</span>
                    <span><strong>Best Parameters:</strong> max_depth=3, n_estimators=150, learning_rate=0.2</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-orange-400 mt-1">•</span>
                    <span><strong>Final Accuracy:</strong> 89% on test set</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-xl p-8">
          <h3 className="text-2xl font-bold text-white mb-4">Why This Dataset?</h3>
          <div className="grid md:grid-cols-2 gap-6 text-gray-300">
            <div>
              <h4 className="text-lg font-semibold text-orange-300 mb-2">Real-World Data</h4>
              <p className="text-sm">
                Amazon product reviews represent real user opinions, making the model practical for actual sentiment analysis applications.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold text-red-300 mb-2">Balanced & Diverse</h4>
              <p className="text-sm">
                The dataset contains a balanced mix of positive and negative reviews with diverse vocabulary and expressions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

