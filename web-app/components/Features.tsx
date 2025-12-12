'use client';

export default function Features() {
  const features = [
    {
      title: '89% Accuracy',
      description: 'Trained on 2000 examples with optimized hyperparameters',
      icon: '🎯',
      color: 'from-orange-500 to-red-500'
    },
    {
      title: 'Real-Time Analysis',
      description: 'Process sentiment in milliseconds with live statistics',
      icon: '⚡',
      color: 'from-red-500 to-orange-500'
    },
    {
      title: 'Interactive Charts',
      description: 'Visualize sentiment distribution with dynamic graphs',
      icon: '📊',
      color: 'from-orange-600 to-red-600'
    },
    {
      title: 'Privacy Guaranteed',
      description: 'Your data never leaves encrypted form during processing',
      icon: '🔒',
      color: 'from-red-600 to-black'
    },
  ];

  return (
    <section className="py-20 px-4 bg-black">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Key Features
          </h2>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-gradient-to-br from-gray-900 to-black border border-gray-800 rounded-xl p-6 hover:border-red-500/50 transition-all duration-300 transform hover:scale-105"
            >
              <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${feature.color} flex items-center justify-center text-3xl mb-4 shadow-lg`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-gray-300 text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

