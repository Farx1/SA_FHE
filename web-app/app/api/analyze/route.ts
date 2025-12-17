import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { text } = await request.json();

    if (!text || typeof text !== 'string') {
      return NextResponse.json(
        { error: 'Text is required' },
        { status: 400 }
      );
    }

    // Call the Python Flask API server
    const apiUrl = process.env.PYTHON_API_URL || 'http://localhost:8002';
    
    try {
      const response = await fetch(`${apiUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (response.ok) {
        const data = await response.json();
        return NextResponse.json(data);
      } else {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'API request failed');
      }
    } catch (apiError) {
      console.error('Error calling Python API:', apiError);
      
      // Fallback: Simple keyword-based sentiment (temporary)
      const lowerText = text.toLowerCase();
      const positiveWords = ['love', 'amazing', 'great', 'excellent', 'best', 'good', 'perfect', 'wonderful', 'fantastic', 'nice', 'awesome'];
      const negativeWords = ['terrible', 'bad', 'worst', 'awful', 'hate', 'disappointed', 'waste', 'poor', 'horrible', 'disgusting'];
      
      const positiveCount = positiveWords.filter(word => lowerText.includes(word)).length;
      const negativeCount = negativeWords.filter(word => lowerText.includes(word)).length;
      
      const isPositive = positiveCount > negativeCount || (positiveCount === 0 && negativeCount === 0);
      const confidence = Math.min(95, 70 + Math.abs(positiveCount - negativeCount) * 5);
      
      return NextResponse.json({
        sentiment: isPositive ? 'Positive' : 'Negative',
        confidence: confidence,
        proba_negative: isPositive ? (100 - confidence) / 100 : confidence / 100,
        proba_positive: isPositive ? confidence / 100 : (100 - confidence) / 100,
        processing_time: 0.001,
        note: 'Using fallback analysis (Python API not available)'
      });
    }

  } catch (error) {
    console.error('Error analyzing sentiment:', error);
    return NextResponse.json(
      { error: 'Failed to analyze sentiment' },
      { status: 500 }
    );
  }
}

