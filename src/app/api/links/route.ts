import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const encodedUrl = searchParams.get('url');
  
  if (!encodedUrl) {
    return NextResponse.json({ error: 'Missing URL parameter' }, { status: 400 });
  }

  try {
    // Decode the Base64 URL
    const realUrl = atob(encodedUrl);
    
    // Validate URL format
    const urlObj = new URL(realUrl);
    if (!urlObj.protocol.startsWith('http')) {
      throw new Error('Invalid URL protocol');
    }

    // Redirect to the real URL
    return NextResponse.redirect(realUrl, 302);
  } catch (error) {
    return NextResponse.json({ error: 'Invalid URL' }, { status: 400 });
  }
}
