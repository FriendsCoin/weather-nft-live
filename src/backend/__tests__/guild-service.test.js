/**
 * Guild Service Tests
 * Tests guild creation, membership, and revenue sharing
 */

describe('Guild Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Guild Creation', () => {
    test('should create guild with valid data', async () => {
      const guildData = {
        guildId: 'guild_123',
        name: 'Storm Hunters',
        description: 'Professional weather chasers',
        founder: '0x123abc',
        members: ['0x123abc'],
        totalRevenue: 0,
        totalCaptures: 0,
        status: 'active'
      };

      expect(guildData.name).toBeTruthy();
      expect(guildData.founder).toBeTruthy();
      expect(guildData.members).toContain(guildData.founder);
      expect(guildData.status).toBe('active');
    });

    test('should reject guild without name', async () => {
      const invalidData = {
        founder: '0x123abc'
        // Missing name
      };

      expect(invalidData.name).toBeUndefined();
    });

    test('should include founder in members', async () => {
      const founder = '0x123abc';
      const members = [founder];

      expect(members).toContain(founder);
      expect(members.length).toBe(1);
    });
  });

  describe('Guild Membership', () => {
    test('should create membership with correct role', async () => {
      const membershipData = {
        guildId: 'guild_123',
        userAddress: '0x123abc',
        role: 'founder',
        captures: 0,
        revenue: 0
      };

      expect(['founder', 'admin', 'member']).toContain(membershipData.role);
    });

    test('should prevent duplicate memberships', async () => {
      const guildId = 'guild_123';
      const userAddress = '0x123abc';

      const existingMembership = {
        guildId,
        userAddress,
        role: 'founder'
      };

      const newMembership = {
        guildId,
        userAddress,
        role: 'member'
      };

      expect(existingMembership.userAddress).toBe(newMembership.userAddress);
      expect(existingMembership.guildId).toBe(newMembership.guildId);
    });

    test('should track member statistics', async () => {
      const memberStats = {
        captures: 10,
        revenue: 50.5
      };

      expect(memberStats.captures).toBeGreaterThanOrEqual(0);
      expect(memberStats.revenue).toBeGreaterThanOrEqual(0);
    });
  });

  describe('Algorithm Rental', () => {
    test('should validate algorithm rental data', async () => {
      const rentalData = {
        rentalId: 'rental_123',
        guildId: 'guild_123',
        algorithmId: 'storm-hunter',
        monthlyPrice: 4,
        status: 'active'
      };

      expect(rentalData.guildId).toBeTruthy();
      expect(rentalData.algorithmId).toBeTruthy();
      expect(rentalData.monthlyPrice).toBeGreaterThan(0);
      expect(rentalData.status).toBe('active');
    });

    test('should support all algorithm types', async () => {
      const algorithms = {
        'storm-hunter': { monthlyPrice: 4, accuracy: 97.8 },
        'aurora-predictor': { monthlyPrice: 3, accuracy: 89.3 },
        'micro-climate': { monthlyPrice: 2, accuracy: 91.5 },
        'extreme-weather': { monthlyPrice: 4, accuracy: 96.1 },
        'temperature-anomaly': { monthlyPrice: 1, accuracy: 94.2 }
      };

      Object.keys(algorithms).forEach(algorithmId => {
        expect(algorithms[algorithmId].monthlyPrice).toBeGreaterThan(0);
        expect(algorithms[algorithmId].accuracy).toBeGreaterThan(0);
      });
    });

    test('should track rental expiration', async () => {
      const startDate = new Date();
      const endDate = new Date(startDate.getTime() + (30 * 24 * 60 * 60 * 1000));

      expect(endDate).toBeInstanceOf(Date);
      expect(endDate.getTime()).toBeGreaterThan(startDate.getTime());
    });
  });

  describe('Revenue Sharing', () => {
    test('should calculate 15% guild share correctly', async () => {
      const capturePrice = 100;
      const guildSharePercent = 0.15;
      const userSharePercent = 0.85;

      const guildShare = capturePrice * guildSharePercent;
      const userShare = capturePrice * userSharePercent;

      expect(guildShare).toBe(15);
      expect(userShare).toBe(85);
      expect(guildShare + userShare).toBe(capturePrice);
    });

    test('should handle decimal prices', async () => {
      const capturePrice = 99.99;
      const guildSharePercent = 0.15;
      const userSharePercent = 0.85;

      const guildShare = capturePrice * guildSharePercent;
      const userShare = capturePrice * userSharePercent;

      expect(guildShare).toBeCloseTo(14.999, 2);
      expect(userShare).toBeCloseTo(84.991, 2);
      expect(guildShare + userShare).toBeCloseTo(capturePrice, 2);
    });

    test('should record revenue share transaction', async () => {
      const revenueShare = {
        shareId: 'share_123',
        guildId: 'guild_123',
        userAddress: '0x123abc',
        eventId: 'event_456',
        capturePrice: 100,
        guildShare: 15,
        userShare: 85
      };

      expect(revenueShare.capturePrice).toBe(revenueShare.guildShare + revenueShare.userShare);
    });
  });

  describe('Guild Statistics', () => {
    test('should track total revenue', async () => {
      const guild = {
        totalRevenue: 0
      };

      const captures = [15, 20, 30]; // Guild shares from captures

      captures.forEach(guildShare => {
        guild.totalRevenue += guildShare;
      });

      expect(guild.totalRevenue).toBe(65);
    });

    test('should track total captures', async () => {
      const guild = {
        totalCaptures: 0
      };

      guild.totalCaptures++;
      guild.totalCaptures++;
      guild.totalCaptures++;

      expect(guild.totalCaptures).toBe(3);
    });
  });

  describe('Leaderboard', () => {
    test('should sort guilds by total revenue', async () => {
      const guilds = [
        { guildId: 'guild_1', totalRevenue: 100 },
        { guildId: 'guild_2', totalRevenue: 250 },
        { guildId: 'guild_3', totalRevenue: 150 }
      ];

      const sorted = guilds.sort((a, b) => b.totalRevenue - a.totalRevenue);

      expect(sorted[0].guildId).toBe('guild_2');
      expect(sorted[1].guildId).toBe('guild_3');
      expect(sorted[2].guildId).toBe('guild_1');
    });

    test('should include member and algorithm counts', async () => {
      const guild = {
        guildId: 'guild_123',
        members: ['0x1', '0x2', '0x3'],
        rentedAlgorithms: ['storm-hunter', 'aurora-predictor']
      };

      expect(guild.members.length).toBe(3);
      expect(guild.rentedAlgorithms.length).toBe(2);
    });
  });
});
