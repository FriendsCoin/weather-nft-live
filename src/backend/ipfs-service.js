#!/usr/bin/env node

/**
 * IPFS Service for WeatherNFT
 * Handles NFT metadata and image storage on IPFS
 * Supports both local IPFS node and Pinata pinning service
 */

const axios = require('axios');
const FormData = require('form-data');

class IPFSService {
  constructor(config = {}) {
    this.config = {
      provider: config.provider || 'pinata', // 'pinata' or 'infura' or 'local'
      pinataApiKey: config.pinataApiKey || process.env.PINATA_API_KEY,
      pinataSecretKey: config.pinataSecretKey || process.env.PINATA_SECRET_KEY,
      infuraProjectId: config.infuraProjectId || process.env.INFURA_PROJECT_ID,
      infuraProjectSecret: config.infuraProjectSecret || process.env.INFURA_PROJECT_SECRET,
      localNodeUrl: config.localNodeUrl || 'http://localhost:5001'
    };

    this.baseGateway = this.config.provider === 'pinata'
      ? 'https://gateway.pinata.cloud/ipfs/'
      : 'https://ipfs.io/ipfs/';
  }

  /**
   * Upload image buffer to IPFS
   * @param {Buffer} imageBuffer - Image data
   * @param {string} filename - Original filename
   * @returns {Promise<{hash: string, url: string}>}
   */
  async uploadImage(imageBuffer, filename) {
    try {
      if (this.config.provider === 'pinata') {
        return await this._uploadToPinata(imageBuffer, filename, 'image');
      } else if (this.config.provider === 'infura') {
        return await this._uploadToInfura(imageBuffer, filename);
      } else {
        return await this._uploadToLocalNode(imageBuffer, filename);
      }
    } catch (error) {
      console.error('❌ IPFS image upload failed:', error.message);
      throw new Error(`IPFS upload failed: ${error.message}`);
    }
  }

  /**
   * Upload JSON metadata to IPFS
   * @param {Object} metadata - NFT metadata object
   * @returns {Promise<{hash: string, url: string}>}
   */
  async uploadMetadata(metadata) {
    try {
      const jsonBuffer = Buffer.from(JSON.stringify(metadata, null, 2));

      if (this.config.provider === 'pinata') {
        return await this._uploadToPinata(jsonBuffer, 'metadata.json', 'metadata');
      } else if (this.config.provider === 'infura') {
        return await this._uploadToInfura(jsonBuffer, 'metadata.json');
      } else {
        return await this._uploadToLocalNode(jsonBuffer, 'metadata.json');
      }
    } catch (error) {
      console.error('❌ IPFS metadata upload failed:', error.message);
      throw new Error(`Metadata upload failed: ${error.message}`);
    }
  }

  /**
   * Generate NFT metadata in standard format
   * @param {Object} params - Metadata parameters
   * @returns {Object} Formatted NFT metadata
   */
  generateMetadata(params) {
    const {
      name,
      description,
      imageHash,
      weatherData,
      eventData,
      location,
      captureTimestamp,
      rarity,
      algorithm
    } = params;

    return {
      name: name || `WeatherNFT #${eventData.id}`,
      description: description || this._generateDescription(weatherData, eventData, location),
      image: `ipfs://${imageHash}`,
      external_url: `https://weathernft.live/nft/${eventData.id}`,
      attributes: [
        {
          trait_type: 'Event Type',
          value: eventData.type
        },
        {
          trait_type: 'Rarity',
          value: rarity
        },
        {
          trait_type: 'Temperature',
          value: weatherData.temperature,
          display_type: 'number'
        },
        {
          trait_type: 'Wind Speed',
          value: weatherData.windSpeed,
          display_type: 'number'
        },
        {
          trait_type: 'Humidity',
          value: weatherData.humidity,
          display_type: 'number'
        },
        {
          trait_type: 'Pressure',
          value: weatherData.pressure,
          display_type: 'number'
        },
        {
          trait_type: 'Location',
          value: `${location.city}, ${location.country}`
        },
        {
          trait_type: 'AI Algorithm',
          value: algorithm
        },
        {
          trait_type: 'Capture Date',
          value: new Date(captureTimestamp).toISOString().split('T')[0]
        },
        {
          trait_type: 'Latitude',
          value: location.lat,
          display_type: 'number'
        },
        {
          trait_type: 'Longitude',
          value: location.lng,
          display_type: 'number'
        }
      ],
      properties: {
        weather: weatherData,
        event: eventData,
        location: location,
        timestamp: captureTimestamp
      }
    };
  }

  /**
   * Upload to Pinata
   * @private
   */
  async _uploadToPinata(buffer, filename, type = 'file') {
    if (!this.config.pinataApiKey || !this.config.pinataSecretKey) {
      throw new Error('Pinata API credentials not configured');
    }

    const formData = new FormData();
    formData.append('file', buffer, { filename });

    const pinataMetadata = JSON.stringify({
      name: filename,
      keyvalues: {
        type: type,
        project: 'WeatherNFT',
        timestamp: Date.now()
      }
    });
    formData.append('pinataMetadata', pinataMetadata);

    const response = await axios.post(
      'https://api.pinata.cloud/pinning/pinFileToIPFS',
      formData,
      {
        headers: {
          'Content-Type': `multipart/form-data; boundary=${formData._boundary}`,
          'pinata_api_key': this.config.pinataApiKey,
          'pinata_secret_api_key': this.config.pinataSecretKey
        },
        maxBodyLength: Infinity
      }
    );

    const hash = response.data.IpfsHash;
    return {
      hash: hash,
      url: `${this.baseGateway}${hash}`,
      pinataUrl: `https://gateway.pinata.cloud/ipfs/${hash}`
    };
  }

  /**
   * Upload to Infura
   * @private
   */
  async _uploadToInfura(buffer, filename) {
    if (!this.config.infuraProjectId || !this.config.infuraProjectSecret) {
      throw new Error('Infura credentials not configured');
    }

    const formData = new FormData();
    formData.append('file', buffer, { filename });

    const auth = Buffer.from(
      `${this.config.infuraProjectId}:${this.config.infuraProjectSecret}`
    ).toString('base64');

    const response = await axios.post(
      'https://ipfs.infura.io:5001/api/v0/add',
      formData,
      {
        headers: {
          'Authorization': `Basic ${auth}`,
          ...formData.getHeaders()
        }
      }
    );

    const hash = response.data.Hash;
    return {
      hash: hash,
      url: `${this.baseGateway}${hash}`,
      infuraUrl: `https://ipfs.infura.io/ipfs/${hash}`
    };
  }

  /**
   * Upload to local IPFS node
   * @private
   */
  async _uploadToLocalNode(buffer, filename) {
    const formData = new FormData();
    formData.append('file', buffer, { filename });

    const response = await axios.post(
      `${this.config.localNodeUrl}/api/v0/add`,
      formData,
      {
        headers: formData.getHeaders()
      }
    );

    const hash = response.data.Hash;
    return {
      hash: hash,
      url: `${this.baseGateway}${hash}`,
      localUrl: `${this.config.localNodeUrl}/ipfs/${hash}`
    };
  }

  /**
   * Generate description from weather data
   * @private
   */
  _generateDescription(weatherData, eventData, location) {
    return `A unique weather NFT capturing a ${eventData.type} event in ${location.city}, ${location.country}. ` +
      `Recorded on ${new Date(eventData.timestamp).toLocaleString()} with ${weatherData.temperature}°C, ` +
      `${weatherData.windSpeed} km/h wind, and ${weatherData.humidity}% humidity. ` +
      `This moment was detected by our AI weather algorithms and immortalized as a one-of-a-kind NFT.`;
  }

  /**
   * Get IPFS URL from hash
   * @param {string} hash - IPFS hash
   * @returns {string} Full IPFS URL
   */
  getIpfsUrl(hash) {
    return `${this.baseGateway}${hash}`;
  }

  /**
   * Test IPFS connection
   * @returns {Promise<boolean>}
   */
  async testConnection() {
    try {
      if (this.config.provider === 'pinata') {
        const response = await axios.get(
          'https://api.pinata.cloud/data/testAuthentication',
          {
            headers: {
              'pinata_api_key': this.config.pinataApiKey,
              'pinata_secret_api_key': this.config.pinataSecretKey
            }
          }
        );
        console.log('✅ Pinata connection successful:', response.data.message);
        return true;
      } else if (this.config.provider === 'local') {
        const response = await axios.post(`${this.config.localNodeUrl}/api/v0/version`);
        console.log('✅ Local IPFS node connected:', response.data.Version);
        return true;
      }
      return true;
    } catch (error) {
      console.error('❌ IPFS connection test failed:', error.message);
      return false;
    }
  }
}

module.exports = IPFSService;
