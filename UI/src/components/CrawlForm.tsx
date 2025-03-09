'use client';

import { useState } from 'react';

export default function CrawlForm() {
  const [url, setUrl] = useState('');
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus(null);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/crawl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error('Failed to start crawling');
      }

      const data = await response.json();
      setStatus(data.message);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label
            htmlFor="url"
            className="block text-sm font-medium text-gray-700 dark:text-gray-300"
          >
            Website URL
          </label>
          <input
            type="url"
            id="url"
            value={url}
            onChange={e => setUrl(e.target.value)}
            placeholder="https://example.com"
            className="mt-1 block w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 dark:bg-blue-500 text-white p-2 rounded-md hover:bg-blue-700 dark:hover:bg-blue-600 transition"
        >
          Start Crawling
        </button>
      </form>

      {status && (
        <div className="mt-4 p-2 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-md text-center">
          {status}
        </div>
      )}
      {error && (
        <div className="mt-4 p-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-md text-center">
          {error}
        </div>
      )}
    </div>
  );
}
