/** @type {import('next').NextConfig} */
const nextConfig = {
	async rewrites() {
		return [
			{
				source: '/api/map',
				destination: 'http://localhost:5001/api/map',
			},
		];
	},
};

module.exports = nextConfig;
