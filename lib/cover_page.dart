import 'dart:math';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

// ── Color Palette ──────────────────────────────────────────────────────────
const _kBgDark = Color(0xFF0B1020);
const _kBgCard = Color(0xFF131A2B);
const _kBgCardLight = Color(0xFF1B243A);
const _kGreen = Color(0xFF5B8CFF);
const _kGreenGlow = Color(0x1F5B8CFF);
const _kTextPrimary = Color(0xFFF2F5FF);
const _kTextSecondary = Color(0xFFA8B3CF);
const _kBorderGreen = Color(0xFF33415F);

// ── Cover Page ─────────────────────────────────────────────────────────────
class CoverPage extends StatefulWidget {
  const CoverPage({super.key});

  @override
  State<CoverPage> createState() => _CoverPageState();
}

class _CoverPageState extends State<CoverPage> {
  final ScrollController _scrollCtrl = ScrollController();

  @override
  void dispose() {
    _scrollCtrl.dispose();
    super.dispose();
  }

  void _navigateToLogin() {
    Navigator.of(context).pushNamed('/login');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _kBgDark,
      body: Stack(
        children: [
          const Positioned.fill(child: _BackdropGradient()),
          // Main scrollable content
          SingleChildScrollView(
            controller: _scrollCtrl,
            physics: const BouncingScrollPhysics(),
            child: Column(
              children: [
                _HeroSection(
                  onLaunch: _navigateToLogin,
                ),
                const _ChallengesSection(),
                const _InnovationSection(),
                const _FeaturesGridSection(),
                _CTASection(onLaunch: _navigateToLogin),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ════════════════════════════════════════════════════════════════════════════
//  PARTICLE FIELD (animated background dots)
// ════════════════════════════════════════════════════════════════════════════
class _BackdropGradient extends StatefulWidget {
  const _BackdropGradient();

  @override
  State<_BackdropGradient> createState() => _BackdropGradientState();
}

class _BackdropGradientState extends State<_BackdropGradient>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 12),
    )..repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _ctrl,
      builder: (context, _) {
        final t = _ctrl.value * 2 * pi;
        return Stack(
          children: [
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment(-0.2 + sin(t * 0.3) * 0.25, -1),
                  end: Alignment(0.2 + cos(t * 0.25) * 0.25, 1),
                  colors: [
                    Color(0xFF0B1020),
                    Color(0xFF0A0F1D),
                    Color(0xFF080C18),
                  ],
                ),
              ),
            ),
            Positioned(
              top: -120 + sin(t) * 28,
              right: -80 + cos(t * 0.9) * 36,
              child: Container(
                width: 320,
                height: 320,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  color: Color(0x365B8CFF),
                ),
              ),
            ),
            Positioned(
              top: 280 + cos(t * 1.1) * 24,
              left: -120 + sin(t * 0.8) * 30,
              child: Container(
                width: 260,
                height: 260,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  color: Color(0x285B8CFF),
                ),
              ),
            ),
            Positioned(
              top: 140 + sin(t * 1.5) * 18,
              left: 420 + cos(t * 1.2) * 24,
              child: Container(
                width: 180,
                height: 180,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  color: Color(0x1F8B5CF6),
                ),
              ),
            ),
            Positioned(
              bottom: -100 + cos(t * 1.3) * 20,
              right: 260 + sin(t * 0.7) * 26,
              child: Container(
                width: 220,
                height: 220,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  color: Color(0x1B38BDF8),
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}

// ════════════════════════════════════════════════════════════════════════════
//  SECTION 1 — HERO
// ════════════════════════════════════════════════════════════════════════════
class _HeroSection extends StatelessWidget {
  const _HeroSection({required this.onLaunch});
  final VoidCallback onLaunch;

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    final isWide = w > 800;

    return Container(
      constraints: const BoxConstraints(minHeight: 700),
      padding: EdgeInsets.symmetric(
        horizontal: isWide ? 80 : 24,
        vertical: 60,
      ),
      child:
          isWide
              ? Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Expanded(flex: 5, child: _heroLeft(context)),
                  const SizedBox(width: 48),
                  Expanded(
                    flex: 4,
                    child: _heroRight(),
                  ),
                ],
              )
              : Column(
                children: [
                  _heroLeft(context),
                  const SizedBox(height: 40),
                  _heroRight(),
                ],
              ),
    );
  }

  Widget _heroLeft(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        // App name
        Text(
          'HackHub',
          style: GoogleFonts.outfit(
            fontSize: 64,
            fontWeight: FontWeight.w800,
            color: _kTextPrimary,
            letterSpacing: -1,
            height: 1.1,
          ),
        ),
        const SizedBox(height: 8),
        // Tagline
        Text(
          'Build Better Open-Source\nWorkflows',
          style: GoogleFonts.outfit(
            fontSize: 36,
            fontWeight: FontWeight.w600,
            color: _kTextPrimary.withValues(alpha: 0.85),
            height: 1.3,
          ),
        ),
        const SizedBox(height: 20),
        // Description
        Text(
          'Discover the perfect GitHub repositories with precision filters, '
          'collaborate on open-source issues, enhance your READMEs with AI, '
          'and find like-minded hackers for your next big project.',
          style: GoogleFonts.inter(
            fontSize: 16,
            color: _kTextSecondary,
            height: 1.7,
          ),
        ),
        const SizedBox(height: 36),
        // Buttons
        Wrap(
          spacing: 16,
          runSpacing: 12,
          children: [
            _HeroButton(
              label: 'Launch App',
              icon: Icons.arrow_forward,
              onTap: onLaunch,
              isPrimary: true,
            ),
            _HeroButton(
              label: 'Watch Demo',
              icon: Icons.play_arrow,
              onTap: () {},
            ),
          ],
        ),
        const SizedBox(height: 48),
        // Stats
        Wrap(
          spacing: 32,
          runSpacing: 16,
          children: const [
            _StatItem(value: '50K+', label: 'REPOS INDEXED'),
            _StatItem(value: '10+', label: 'SMART FILTERS'),
            _StatItem(value: '24/7', label: 'ALWAYS ONLINE'),
          ],
        ),
      ],
    );
  }

  Widget _heroRight() {
    return Container(
      constraints: const BoxConstraints(maxWidth: 460),
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: _kBgCard,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: _kBorderGreen),
        boxShadow: const [
          BoxShadow(
            color: Color(0x22000000),
            blurRadius: 24,
            offset: Offset(0, 14),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Container(
                width: 10,
                height: 10,
                decoration: const BoxDecoration(
                  color: Color(0xFFFF5F57),
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 6),
              Container(
                width: 10,
                height: 10,
                decoration: const BoxDecoration(
                  color: Color(0xFFFFBD2E),
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 6),
              Container(
                width: 10,
                height: 10,
                decoration: const BoxDecoration(
                  color: Color(0xFF28C840),
                  shape: BoxShape.circle,
                ),
              ),
              const Spacer(),
              Text(
                'Workflow Snapshot',
                style: GoogleFonts.inter(
                  color: _kTextSecondary,
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          _previewRow(
            icon: Icons.manage_search,
            title: 'Repository Match',
            value: '238 curated results',
          ),
          const SizedBox(height: 12),
          _previewRow(
            icon: Icons.task_alt,
            title: 'Issue Pipeline',
            value: '16 beginner-friendly',
          ),
          const SizedBox(height: 12),
          _previewRow(
            icon: Icons.groups_2_outlined,
            title: 'Team Availability',
            value: '4 collaborators online',
          ),
          const SizedBox(height: 18),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              color: _kBgCardLight,
            ),
            child: Text(
              'Tip: Start with language + issue difficulty filters to reduce noise quickly.',
              style: GoogleFonts.inter(
                color: _kTextSecondary,
                fontSize: 12,
                height: 1.5,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _previewRow({
    required IconData icon,
    required String title,
    required String value,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: _kBgCardLight,
        borderRadius: BorderRadius.circular(14),
      ),
      child: Row(
        children: [
          Icon(icon, color: _kGreen, size: 19),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              title,
              style: GoogleFonts.inter(
                color: _kTextPrimary,
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          Text(
            value,
            style: GoogleFonts.inter(
              color: _kTextSecondary,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}

// ── Stat Item ──────────────────────────────────────────────────────────────
class _StatItem extends StatelessWidget {
  const _StatItem({required this.value, required this.label});
  final String value;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          value,
          style: GoogleFonts.outfit(
            fontSize: 32,
            fontWeight: FontWeight.w700,
            color: _kTextPrimary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 11,
            color: _kTextSecondary,
            letterSpacing: 1.5,
          ),
        ),
      ],
    );
  }
}

// ── Glow Button ────────────────────────────────────────────────────────────
class _HeroButton extends StatefulWidget {
  const _HeroButton({
    required this.label,
    required this.icon,
    required this.onTap,
    this.isPrimary = false,
  });
  final String label;
  final IconData icon;
  final VoidCallback onTap;
  final bool isPrimary;

  @override
  State<_HeroButton> createState() => _HeroButtonState();
}

class _HeroButtonState extends State<_HeroButton> {
  bool _hovering = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovering = true),
      onExit: (_) => setState(() => _hovering = false),
      child: GestureDetector(
        onTap: widget.onTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 250),
          padding: const EdgeInsets.symmetric(horizontal: 26, vertical: 15),
          decoration: BoxDecoration(
            color: widget.isPrimary ? _kGreen : _kBgCardLight,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: widget.isPrimary ? _kGreen : _kBorderGreen,
              width: 1.2,
            ),
            boxShadow: [
              BoxShadow(
                color: widget.isPrimary
                    ? _kGreen.withValues(alpha: _hovering ? 0.24 : 0.12)
                    : const Color(0x22000000),
                blurRadius: _hovering ? 16 : 8,
                offset: const Offset(0, 5),
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                widget.icon,
                size: 18,
                color: widget.isPrimary ? _kBgDark : _kTextPrimary,
              ),
              const SizedBox(width: 10),
              Text(
                widget.label,
                style: GoogleFonts.inter(
                  color: widget.isPrimary ? _kBgDark : _kTextPrimary,
                  fontWeight: FontWeight.w700,
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ════════════════════════════════════════════════════════════════════════════
//  SECTION 2 — CHALLENGES
// ════════════════════════════════════════════════════════════════════════════
class _ChallengesSection extends StatelessWidget {
  const _ChallengesSection();

  static const _challenges = [
    _ChallengeData(
      Icons.search_off,
      'Repo Discovery',
      'Finding the right GitHub repos among millions is overwhelming — most search tools return too many irrelevant results.',
    ),
    _ChallengeData(
      Icons.bug_report_outlined,
      'Issue Overload',
      'Open-source contributors struggle to find meaningful issues that match their skill level and interests.',
    ),
    _ChallengeData(
      Icons.person_search_outlined,
      'Team Finding',
      'Building a hackathon team or finding collaborators with the right mindset is hard without a dedicated platform.',
    ),
    _ChallengeData(
      Icons.description_outlined,
      'README Quality',
      'Many repositories lack well-structured READMEs, making it difficult for new contributors to get started.',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    final isWide = w > 800;
    return Container(
      width: double.infinity,
      padding: EdgeInsets.symmetric(
        horizontal: isWide ? 80 : 24,
        vertical: 80,
      ),
      child: Column(
        children: [
          _SectionBadge(label: 'THE CHALLENGE'),
          const SizedBox(height: 16),
          Text(
            'The Real-World Problem',
            textAlign: TextAlign.center,
            style: GoogleFonts.outfit(
              fontSize: 48,
              fontWeight: FontWeight.w700,
              color: _kTextPrimary,
            ),
          ),
          const SizedBox(height: 48),
          isWide
              ? Row(
                  children: _challenges
                      .map(
                        (c) => Expanded(
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 8),
                            child: _ChallengeCard(data: c),
                          ),
                        ),
                      )
                      .toList(),
                )
              : Column(
                  children: _challenges
                      .map(
                        (c) => Padding(
                          padding: const EdgeInsets.only(bottom: 16),
                          child: _ChallengeCard(data: c),
                        ),
                      )
                      .toList(),
                ),
        ],
      ),
    );
  }
}

class _ChallengeData {
  const _ChallengeData(this.icon, this.title, this.description);
  final IconData icon;
  final String title;
  final String description;
}

class _ChallengeCard extends StatefulWidget {
  const _ChallengeCard({required this.data});
  final _ChallengeData data;

  @override
  State<_ChallengeCard> createState() => _ChallengeCardState();
}

class _ChallengeCardState extends State<_ChallengeCard> {
  bool _hovering = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovering = true),
      onExit: (_) => setState(() => _hovering = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        padding: const EdgeInsets.all(28),
        decoration: BoxDecoration(
          color: _hovering ? _kBgCardLight : _kBgCard,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: _hovering ? _kGreen.withValues(alpha: 0.5) : _kBorderGreen,
          ),
          boxShadow: _hovering
              ? [BoxShadow(color: _kGreenGlow, blurRadius: 24)]
              : [],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _kBgDark,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(widget.data.icon, color: _kGreen, size: 28),
            ),
            const SizedBox(height: 20),
            Text(
              widget.data.title,
              style: GoogleFonts.outfit(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: _kGreen,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              widget.data.description,
              style: GoogleFonts.inter(
                fontSize: 14,
                color: _kTextSecondary,
                height: 1.6,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ════════════════════════════════════════════════════════════════════════════
//  SECTION 3 — INNOVATION
// ════════════════════════════════════════════════════════════════════════════
class _InnovationSection extends StatelessWidget {
  const _InnovationSection();

  static const _features = [
    'Precision Repo Search: Discover hidden-gem repositories with advanced multi-filter queries that return only the most relevant results.',
    'Smart Issue Matching: Browse and filter open-source issues by difficulty, language, and label to find your perfect contribution.',
    'README Enhancer: AI-powered README generation and improvement to make your repos stand out.',
    'Hackathon Team Builder: Find like-minded developers by filtering profiles based on skills, interests, and availability.',
  ];

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    final isWide = w > 800;

    return Container(
      width: double.infinity,
      padding: EdgeInsets.symmetric(
        horizontal: isWide ? 80 : 24,
        vertical: 80,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [          Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 920),
              child: Column(
                children: [
                  _SectionBadge(label: 'OUR INNOVATION'),
                  const SizedBox(height: 16),
                  Text(
                    'Intelligent Developer\nSupport',
                    textAlign: TextAlign.center,
                    style: GoogleFonts.outfit(
                      fontSize: 48,
                      fontWeight: FontWeight.w700,
                      color: _kTextPrimary,
                      height: 1.2,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'HackHub transforms how developers discover repositories, collaborate on issues, '
                    'and build teams. Our platform does not just search - it provides complete workflow '
                    'support from discovery to deployment, accessible to developers of every level.',
                    textAlign: TextAlign.center,
                    style: GoogleFonts.inter(
                      fontSize: 18,
                      color: _kTextSecondary,
                      height: 1.7,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 40),
          Column(
            children: _features.map((f) => _FeatureCheckItem(text: f)).toList(),
          ),
        ],
      ),
    );
  }
}

class _FeatureCheckItem extends StatelessWidget {
  const _FeatureCheckItem({required this.text});
  final String text;

  @override
  Widget build(BuildContext context) {
    final parts = text.split(': ');
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _kBgCard,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: _kBorderGreen),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            margin: const EdgeInsets.only(top: 2),
            padding: const EdgeInsets.all(4),
            decoration: const BoxDecoration(
              color: _kGreen,
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.check, color: _kBgDark, size: 14),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: RichText(
              text: TextSpan(
                children: [
                  TextSpan(
                    text: '${parts[0]}: ',
                    style: GoogleFonts.inter(
                      color: _kGreen,
                      fontWeight: FontWeight.w600,
                      fontSize: 18,
                      height: 1.6,
                    ),
                  ),
                  TextSpan(
                    text: parts.length > 1 ? parts[1] : '',
                    style: GoogleFonts.inter(
                      color: _kTextSecondary,
                      fontSize: 16,
                      height: 1.6,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ════════════════════════════════════════════════════════════════════════════
//  SECTION 4 — FEATURES GRID
// ════════════════════════════════════════════════════════════════════════════
class _FeaturesGridSection extends StatelessWidget {
  const _FeaturesGridSection();

  static const _features = [
    _FeatureGridData(
      Icons.manage_search,
      'Precision Search',
      'Advanced multi-filter repo search returns only the most relevant gems you won\'t find elsewhere.',
    ),
    _FeatureGridData(
      Icons.filter_alt_outlined,
      'Smart Filters',
      'Filter repos by stars, language, last updated, issues count and more — with rare-result accuracy.',
    ),
    _FeatureGridData(
      Icons.bug_report_outlined,
      'Issue Tracker',
      'Browse open-source issues linearly, filtered by difficulty and labels, ready for your contribution.',
    ),
    _FeatureGridData(
      Icons.auto_fix_high,
      'README Enhancer',
      'AI-powered README generation that transforms sparse docs into professional, contributor-friendly guides.',
    ),
    _FeatureGridData(
      Icons.groups_outlined,
      'Team Finder',
      'Find like-minded developers for hackathons and projects by filtering profiles, skills, and interests.',
    ),
    _FeatureGridData(
      Icons.handshake_outlined,
      'Repo Collaboration',
      'Seamlessly collaborate on repos, coordinate contributions, and manage team workflows in one place.',
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final w = MediaQuery.of(context).size.width;
    final isWide = w > 800;
    final crossCount = isWide ? 3 : (w > 500 ? 2 : 1);

    return Container(
      width: double.infinity,
      padding: EdgeInsets.symmetric(
        horizontal: isWide ? 80 : 24,
        vertical: 80,
      ),
      child: Column(
        children: [
          _SectionBadge(label: 'CAPABILITIES'),
          const SizedBox(height: 16),
          Text(
            'Powerful Features',
            textAlign: TextAlign.center,
            style: GoogleFonts.outfit(
              fontSize: isWide ? 48 : 38,
              fontWeight: FontWeight.w700,
              color: _kTextPrimary,
            ),
          ),
          const SizedBox(height: 48),
          GridView.count(
            crossAxisCount: crossCount,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            mainAxisSpacing: 14,
            crossAxisSpacing: 14,
            childAspectRatio: isWide ? 2.0 : (w > 500 ? 1.5 : 1.2),
            children: _features.map((f) => _FeatureGridCard(data: f)).toList(),
          ),
        ],
      ),
    );
  }
}

class _FeatureGridData {
  const _FeatureGridData(this.icon, this.title, this.description);
  final IconData icon;
  final String title;
  final String description;
}

class _FeatureGridCard extends StatefulWidget {
  const _FeatureGridCard({required this.data});
  final _FeatureGridData data;

  @override
  State<_FeatureGridCard> createState() => _FeatureGridCardState();
}

class _FeatureGridCardState extends State<_FeatureGridCard> {
  bool _hovering = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovering = true),
      onExit: (_) => setState(() => _hovering = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: _hovering ? _kBgCardLight : _kBgCard,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: _hovering ? _kGreen.withValues(alpha: 0.5) : _kBorderGreen,
          ),
          boxShadow: _hovering
              ? [BoxShadow(color: _kGreenGlow, blurRadius: 24)]
              : [],
        ),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: _kBgDark,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(widget.data.icon, color: _kGreen, size: 24),
              ),
              const SizedBox(height: 14),
              Text(
                widget.data.title,
                style: GoogleFonts.outfit(
                  fontSize: 22,
                  fontWeight: FontWeight.w600,
                  color: _kGreen,
                ),
              ),
              const SizedBox(height: 6),
              Text(
                widget.data.description,
                style: GoogleFonts.inter(
                  fontSize: 15,
                  color: _kTextSecondary,
                  height: 1.5,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ════════════════════════════════════════════════════════════════════════════
//  SECTION 5 — CTA FOOTER
// ════════════════════════════════════════════════════════════════════════════
class _CTASection extends StatelessWidget {
  const _CTASection({required this.onLaunch});
  final VoidCallback onLaunch;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 80),
      child: Column(
        children: [
          Text(
            'Ready to Build\nSomething Amazing?',
            textAlign: TextAlign.center,
            style: GoogleFonts.outfit(
              fontSize: 40,
              fontWeight: FontWeight.w700,
              color: _kTextPrimary,
              height: 1.2,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Join thousands of developers using HackHub to discover repos,\nsolve issues, and ship projects faster.',
            textAlign: TextAlign.center,
            style: GoogleFonts.inter(
              fontSize: 16,
              color: _kTextSecondary,
              height: 1.6,
            ),
          ),
          const SizedBox(height: 36),
          _HeroButton(
            label: 'Launch HackHub',
            icon: Icons.rocket_launch,
            onTap: onLaunch,
            isPrimary: true,
          ),
          const SizedBox(height: 28),
          Wrap(
            spacing: 32,
            runSpacing: 8,
            alignment: WrapAlignment.center,
            children: [
              _checkFact('Free to use'),
              _checkFact('Open-source friendly'),
              _checkFact('Built for hackers'),
            ],
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  Widget _checkFact(String text) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Icon(Icons.check, color: _kGreen, size: 16),
        const SizedBox(width: 6),
        Text(
          text,
          style: GoogleFonts.inter(color: _kTextSecondary, fontSize: 13),
        ),
      ],
    );
  }
}

// ── Reusable Section Badge ─────────────────────────────────────────────────
class _SectionBadge extends StatelessWidget {
  const _SectionBadge({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _kGreen.withValues(alpha: 0.5)),
        color: _kGreenGlow,
      ),
      child: Text(
        label,
        style: GoogleFonts.inter(
          color: _kGreen,
          fontSize: 12,
          fontWeight: FontWeight.w600,
          letterSpacing: 1.5,
        ),
      ),
    );
  }
}


