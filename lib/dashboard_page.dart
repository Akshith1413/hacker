import 'dart:convert';
import 'dart:math';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:hacker/login_page.dart';
import 'package:hacker/settings_page.dart';
import 'package:hacker/models/github_repo.dart';
import 'package:hacker/services/github_service.dart';
import 'package:url_launcher/url_launcher.dart';

// ── Color Palette ─────────────────────────────────────────────────────────────
const _kBgDark = Color(0xFF0B1020);
const _kBgCard = Color(0xFF131A2B);
const _kBgCardLight = Color(0xFF1B243A);
const _kGreen = Color(0xFF5B8CFF);
const _kTextPrimary = Color(0xFFF2F5FF);
const _kTextSecondary = Color(0xFFA8B3CF);
const _kBorderGreen = Color(0xFF33415F);
const _kGold = Color(0xFFFFC107);
const _kPurple = Color(0xFF9C6FFF);

// Grade color helper
Color _gradeColor(String grade) {
  switch (grade) {
    case 'A+': return const Color(0xFF00E676);
    case 'A':  return const Color(0xFF69F0AE);
    case 'B+': return const Color(0xFF40C4FF);
    case 'B':  return const Color(0xFF80D8FF);
    case 'C+': return const Color(0xFFFFD740);
    case 'C':  return const Color(0xFFFFAB40);
    case 'D':  return const Color(0xFFFF6D00);
    default:   return const Color(0xFFFF5252);
  }
}

Color _statusColor(String? status) {
  switch (status?.toLowerCase()) {
    case 'active':       return const Color(0xFF00E676);
    case 'ongoing':      return const Color(0xFF40C4FF);
    case 'slowing down': return const Color(0xFFFFD740);
    case 'started':      return _kPurple;
    case 'finished':     return const Color(0xFFA8B3CF);
    default:             return const Color(0xFFA8B3CF);
  }
}

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> with SingleTickerProviderStateMixin {
  User? _user;
  Map<String, dynamic>? _userData;

  // Search & Filter State
  final TextEditingController _searchController = TextEditingController();
  final GithubService _githubService = GithubService();
  List<GithubRepo> _repos = [];
  String? _selectedTechStack;
  String? _selectedStatus;
  String _sortBy = 'updated';
  bool _excludeForks = false;
  bool _excludeArchived = false;
  bool _isSearching = false;
  String? _errorMessage;
  int _minStars = 0;
  int _minQualityScore = 0;
  bool _showAdvancedFilters = false;

  final List<String> _techStacks = [
    'MERN', 'MEAN', 'Full Stack', 'Machine Learning', 'Data Science', 'Mobile Dev',
    'Flutter', 'React', 'Django', 'Spring', 'DevOps', 'Web3/Blockchain',
    'Go', 'Rust', 'Python', 'JavaScript', 'TypeScript', 'Java', 'Swift', 'Kotlin', 'C++',
    'Game Dev', 'Modern Frontend', 'Backend Strong',
  ];

  final List<String> _statuses = ['Active', 'Ongoing', 'Started', 'Slowing Down', 'Finished'];
  final List<String> _sortOptions = ['updated', 'stars', 'forks', 'quality'];

  late final AnimationController _bgCtrl;

  @override
  void initState() {
    super.initState();
    _bgCtrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 12),
    )..repeat();
    _loadUserData();
  }

  @override
  void dispose() {
    _bgCtrl.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadUserData() async {
    _user = FirebaseAuth.instance.currentUser;
    if (_user != null) {
      try {
        final doc = await FirebaseFirestore.instance.collection('users').doc(_user!.uid).get();
        if (doc.exists && mounted) {
          setState(() => _userData = doc.data());
        }
      } catch (e) {
        debugPrint('Error loading user data: $e');
      }
    }
  }

  Future<void> _searchRepos() async {
    setState(() {
      _isSearching = true;
      _errorMessage = null;
    });

    try {
      final results = await _githubService.searchRepositories(
        _searchController.text,
        techStack: _selectedTechStack,
        status: _selectedStatus?.toLowerCase().replaceAll(' ', '-'),
        minStars: _minStars,
        minQualityScore: _minQualityScore,
        sortBy: _sortBy,
        excludeForks: _excludeForks,
        excludeArchived: _excludeArchived,
      );
      if (mounted) setState(() => _repos = results);
    } catch (e) {
      if (mounted) setState(() => _errorMessage = e.toString());
    } finally {
      if (mounted) setState(() => _isSearching = false);
    }
  }

  Future<void> _signOut() async {
    await FirebaseAuth.instance.signOut();
    if (mounted) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => const LoginPage()),
      );
    }
  }

  void _openSettings() {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (context) => const SettingsPage()),
    );
  }

  Future<void> _launchUrl(String url) async {
    final uri = Uri.parse(url);
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not launch $url')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _kBgDark,
      body: Stack(
        children: [
          // ── Animated Background ───────────────────────────────────────────
          Positioned.fill(
            child: AnimatedBuilder(
              animation: _bgCtrl,
              builder: (context, _) {
                final t = _bgCtrl.value * 2 * pi;
                return Stack(children: [
                  Container(
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [Color(0xFF0B1020), Color(0xFF0A0F1D), Color(0xFF080C18)],
                      ),
                    ),
                  ),
                  Positioned(
                    top: -120 + sin(t) * 28,
                    right: -80 + cos(t * 0.9) * 36,
                    child: Container(
                      width: 320, height: 320,
                      decoration: const BoxDecoration(shape: BoxShape.circle, color: Color(0x365B8CFF)),
                    ),
                  ),
                  Positioned(
                    top: 280 + cos(t * 1.1) * 24,
                    left: -120 + sin(t * 0.8) * 30,
                    child: Container(
                      width: 260, height: 260,
                      decoration: const BoxDecoration(shape: BoxShape.circle, color: Color(0x285B8CFF)),
                    ),
                  ),
                ]);
              },
            ),
          ),

          // ── Content ───────────────────────────────────────────────────────
          Column(
            children: [
              _buildAppBar(),
              _buildSearchSection(),
              Expanded(
                child: _isSearching
                    ? const Center(child: CircularProgressIndicator(color: _kGreen))
                    : _errorMessage != null
                        ? _buildError()
                        : _buildResultsList(),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ── APP BAR ───────────────────────────────────────────────────────────────
  Widget _buildAppBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      color: Colors.transparent,
      child: SafeArea(
        child: Row(
          children: [
            Text('HackHub', style: GoogleFonts.outfit(fontSize: 24, fontWeight: FontWeight.w800, color: _kTextPrimary, letterSpacing: -0.5)),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: _kGreen.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: _kGreen.withOpacity(0.5)),
              ),
              child: Text('ML v2', style: GoogleFonts.inter(fontSize: 10, fontWeight: FontWeight.w700, color: _kGreen, letterSpacing: 1.0)),
            ),
            const Spacer(),
            PopupMenuButton<String>(
              onSelected: (value) {
                if (value == 'settings') _openSettings();
                if (value == 'logout') _signOut();
              },
              offset: const Offset(0, 48),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: const BorderSide(color: _kBorderGreen)),
              color: _kBgCard,
              child: _buildAvatar(18),
              itemBuilder: (context) => [
                _buildMenuItem('settings', Icons.settings, 'Settings'),
                _buildMenuItem('logout', Icons.logout, 'Logout'),
              ],
            ),
          ],
        ),
      ),
    );
  }

  PopupMenuItem<String> _buildMenuItem(String value, IconData icon, String text) {
    return PopupMenuItem(
      value: value,
      child: Row(children: [
        Icon(icon, size: 18, color: _kTextSecondary),
        const SizedBox(width: 12),
        Text(text, style: GoogleFonts.inter(color: _kTextPrimary)),
      ]),
    );
  }

  // ── SEARCH & FILTER SECTION ───────────────────────────────────────────────
  Widget _buildSearchSection() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _kBgCard.withOpacity(0.8),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _kBorderGreen),
        boxShadow: const [BoxShadow(color: Color(0x22000000), blurRadius: 16, offset: Offset(0, 8))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Search bar
          TextField(
            controller: _searchController,
            style: GoogleFonts.inter(color: _kTextPrimary),
            decoration: InputDecoration(
              hintText: 'Search projects, topics, or ideas...',
              hintStyle: GoogleFonts.inter(color: _kTextSecondary.withOpacity(0.6)),
              prefixIcon: const Icon(Icons.search, color: _kTextSecondary),
              suffixIcon: IconButton(
                icon: const Icon(Icons.arrow_forward, color: _kGreen),
                onPressed: _searchRepos,
              ),
              filled: true,
              fillColor: _kBgCardLight,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
              enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: _kBorderGreen)),
              focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: _kGreen)),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
            onSubmitted: (_) => _searchRepos(),
          ),

          const SizedBox(height: 14),
          // Row 1: Tech Stack + Status chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildDropdownFilter(),
                const SizedBox(width: 10),
                ..._statuses.map((s) => _buildStatusChip(s)),
              ],
            ),
          ),

          const SizedBox(height: 12),
          // Row 2: Stars
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                const Icon(Icons.star_outline, color: _kTextSecondary, size: 15),
                const SizedBox(width: 6),
                Text('Stars:', style: GoogleFonts.inter(color: _kTextSecondary, fontSize: 12)),
                const SizedBox(width: 8),
                _buildStarChip(0, 'Any'),
                _buildStarChip(10, '10+'),
                _buildStarChip(100, '100+'),
                _buildStarChip(1000, '1k+'),
                _buildStarChip(5000, '5k+'),
              ],
            ),
          ),

          const SizedBox(height: 10),
          // Advanced Filters toggle
          GestureDetector(
            onTap: () => setState(() => _showAdvancedFilters = !_showAdvancedFilters),
            child: Row(
              children: [
                Icon(_showAdvancedFilters ? Icons.expand_less : Icons.expand_more, color: _kGreen, size: 18),
                const SizedBox(width: 4),
                Text(
                  _showAdvancedFilters ? 'Hide Advanced Filters' : 'Advanced Filters (Quality, Sort, Forks...)',
                  style: GoogleFonts.inter(color: _kGreen, fontSize: 12, fontWeight: FontWeight.w600),
                ),
              ],
            ),
          ),

          if (_showAdvancedFilters) ...[
            const SizedBox(height: 14),
            // Quality score filter
            Row(
              children: [
                const Icon(Icons.auto_awesome, color: _kPurple, size: 15),
                const SizedBox(width: 6),
                Text('Min Quality:', style: GoogleFonts.inter(color: _kTextSecondary, fontSize: 12)),
                const SizedBox(width: 8),
                _buildQualityChip(0, 'Any'),
                _buildQualityChip(50, '50+'),
                _buildQualityChip(65, '65+'),
                _buildQualityChip(80, '80+'),
              ],
            ),
            const SizedBox(height: 12),
            // Sort by
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  const Icon(Icons.sort, color: _kTextSecondary, size: 15),
                  const SizedBox(width: 6),
                  Text('Sort by:', style: GoogleFonts.inter(color: _kTextSecondary, fontSize: 12)),
                  const SizedBox(width: 8),
                  ..._sortOptions.map((s) => _buildSortChip(s)),
                ],
              ),
            ),
            const SizedBox(height: 12),
            // Toggle flags
            Wrap(
              spacing: 10,
              children: [
                _buildToggleChip('Exclude Forks', _excludeForks, (v) => setState(() { _excludeForks = v; _searchRepos(); })),
                _buildToggleChip('Exclude Archived', _excludeArchived, (v) => setState(() { _excludeArchived = v; _searchRepos(); })),
              ],
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildStarChip(int stars, String label) {
    final isSelected = _minStars == stars;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: InkWell(
        onTap: () { setState(() => _minStars = stars); _searchRepos(); },
        borderRadius: BorderRadius.circular(20),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: isSelected ? _kGold.withOpacity(0.2) : _kBgCardLight,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: isSelected ? _kGold : _kBorderGreen),
          ),
          child: Row(children: [
            if (isSelected) ...[const Icon(Icons.star, size: 10, color: _kGold), const SizedBox(width: 4)],
            Text(label, style: GoogleFonts.inter(color: isSelected ? _kGold : _kTextSecondary, fontSize: 11, fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500)),
          ]),
        ),
      ),
    );
  }

  Widget _buildQualityChip(int score, String label) {
    final isSelected = _minQualityScore == score;
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: InkWell(
        onTap: () { setState(() => _minQualityScore = score); _searchRepos(); },
        borderRadius: BorderRadius.circular(20),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: isSelected ? _kPurple.withOpacity(0.2) : _kBgCardLight,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: isSelected ? _kPurple : _kBorderGreen),
          ),
          child: Text(label, style: GoogleFonts.inter(color: isSelected ? _kPurple : _kTextSecondary, fontSize: 11, fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500)),
        ),
      ),
    );
  }

  Widget _buildSortChip(String sortKey) {
    final isSelected = _sortBy == sortKey;
    final labels = {'updated': 'Recent', 'stars': 'Stars', 'forks': 'Forks', 'quality': 'Quality'};
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: InkWell(
        onTap: () { setState(() => _sortBy = sortKey); _searchRepos(); },
        borderRadius: BorderRadius.circular(20),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: isSelected ? _kGreen.withOpacity(0.2) : _kBgCardLight,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: isSelected ? _kGreen : _kBorderGreen),
          ),
          child: Text(labels[sortKey] ?? sortKey, style: GoogleFonts.inter(color: isSelected ? _kGreen : _kTextSecondary, fontSize: 11, fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500)),
        ),
      ),
    );
  }

  Widget _buildStatusChip(String label) {
    final isSelected = _selectedStatus == label;
    final color = _statusColor(label);
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: InkWell(
        onTap: () { setState(() => _selectedStatus = isSelected ? null : label); _searchRepos(); },
        borderRadius: BorderRadius.circular(20),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
          decoration: BoxDecoration(
            color: isSelected ? color.withOpacity(0.2) : _kBgCardLight,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: isSelected ? color : _kBorderGreen),
          ),
          child: Text(label, style: GoogleFonts.inter(color: isSelected ? color : _kTextSecondary, fontSize: 12, fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500)),
        ),
      ),
    );
  }

  Widget _buildToggleChip(String label, bool value, ValueChanged<bool> onChanged) {
    return GestureDetector(
      onTap: () => onChanged(!value),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
        decoration: BoxDecoration(
          color: value ? _kGreen.withOpacity(0.15) : _kBgCardLight,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: value ? _kGreen : _kBorderGreen),
        ),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(value ? Icons.check_circle : Icons.radio_button_unchecked, size: 13, color: value ? _kGreen : _kTextSecondary),
          const SizedBox(width: 5),
          Text(label, style: GoogleFonts.inter(color: value ? _kGreen : _kTextSecondary, fontSize: 11, fontWeight: FontWeight.w500)),
        ]),
      ),
    );
  }

  Widget _buildDropdownFilter() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(
        color: _kBgCardLight,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: _selectedTechStack != null ? _kGreen : _kBorderGreen),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: _selectedTechStack,
          hint: Text('Tech Stack', style: GoogleFonts.inter(color: _kTextSecondary, fontSize: 13)),
          dropdownColor: _kBgCard,
          icon: const Icon(Icons.code, color: _kTextSecondary, size: 18),
          style: GoogleFonts.inter(color: _kTextPrimary, fontSize: 13),
          items: [
            DropdownMenuItem(value: null, child: Text('All Stacks', style: GoogleFonts.inter(color: _kTextSecondary))),
            ..._techStacks.map((stack) => DropdownMenuItem(value: stack, child: Text(stack))),
          ],
          onChanged: (val) { setState(() => _selectedTechStack = val); _searchRepos(); },
        ),
      ),
    );
  }

  // ── RESULTS ───────────────────────────────────────────────────────────────
  Widget _buildError() {
    return Center(
      child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
        const Icon(Icons.error_outline, size: 48, color: Colors.redAccent),
        const SizedBox(height: 12),
        Text('Connection Error', style: GoogleFonts.outfit(color: _kTextPrimary, fontSize: 18, fontWeight: FontWeight.w700)),
        const SizedBox(height: 8),
        Text('Make sure the backend server is running:\n./run_backend.bat', textAlign: TextAlign.center, style: GoogleFonts.inter(color: _kTextSecondary, fontSize: 13)),
      ]),
    );
  }

  Widget _buildResultsList() {
    if (_repos.isEmpty) {
      return Center(
        child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          Icon(Icons.manage_search, size: 64, color: _kTextSecondary.withOpacity(0.3)),
          const SizedBox(height: 16),
          Text(
            _searchController.text.isEmpty ? 'Ready to explore new code?' : 'No matches found.',
            style: GoogleFonts.inter(color: _kTextSecondary, fontSize: 16),
          ),
          if (_searchController.text.isEmpty) ...[
            const SizedBox(height: 8),
            Text('Search for a tech stack or project name above.', style: GoogleFonts.inter(color: _kTextSecondary.withOpacity(0.6), fontSize: 13)),
          ],
        ]),
      );
    }

    return GridView.builder(
      padding: const EdgeInsets.all(20),
      gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 420,
        mainAxisExtent: 300,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: _repos.length,
      itemBuilder: (context, index) => _buildRepoCard(_repos[index]),
    );
  }

  Widget _buildRepoCard(GithubRepo repo) {
    final statusColor = _statusColor(repo.status);

    return Container(
      decoration: BoxDecoration(
        color: _kBgCard,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _kBorderGreen),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.2), blurRadius: 12, offset: const Offset(0, 4))],
      ),
      child: InkWell(
        onTap: () => _launchUrl(repo.htmlUrl),
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(18),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Header row: avatar + name + grade badge ──
              Row(
                children: [
                  CircleAvatar(
                    radius: 14,
                    backgroundImage: repo.ownerAvatarUrl != null ? NetworkImage(repo.ownerAvatarUrl!) : null,
                    backgroundColor: _kBgCardLight,
                    child: repo.ownerAvatarUrl == null ? const Icon(Icons.code, size: 14, color: _kTextSecondary) : null,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(repo.name,
                          style: GoogleFonts.outfit(color: _kGreen, fontSize: 15, fontWeight: FontWeight.w600),
                          overflow: TextOverflow.ellipsis,
                        ),
                        if (repo.status != null)
                          Row(children: [
                            Container(
                              width: 6, height: 6,
                              decoration: BoxDecoration(shape: BoxShape.circle, color: statusColor),
                            ),
                            const SizedBox(width: 4),
                            Text(repo.status!, style: GoogleFonts.inter(color: statusColor, fontSize: 10, fontWeight: FontWeight.w600)),
                          ]),
                      ],
                    ),
                  ),
                  // Grade badge
                  if (repo.qualityDetail != null)
                    _buildGradeBadge(repo.qualityDetail!.grade),
                ],
              ),

              const SizedBox(height: 10),

              // ── Description ──
              Expanded(
                child: Text(
                  repo.description.isNotEmpty ? repo.description : 'No description provided.',
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: GoogleFonts.inter(color: _kTextSecondary, fontSize: 12, height: 1.5),
                ),
              ),

              const SizedBox(height: 10),

              // ── Quality Score Bar ──
              if (repo.qualityScore != null) _buildQualityBar(repo.qualityScore!),

              const SizedBox(height: 10),

              // ── Stats row: stars / forks / issues ──
              Row(children: [
                _buildStatBadge(Icons.star_rounded, '${repo.stars}', Colors.amber),
                const SizedBox(width: 10),
                _buildStatBadge(Icons.fork_right, '${repo.forks}', _kTextSecondary),
                const SizedBox(width: 10),
                _buildStatBadge(Icons.bug_report_outlined, '${repo.openIssuesCount}', const Color(0xFFFF6B6B)),
              ]),

              const SizedBox(height: 10),

              // ── Tech Stack + Join button ──
              Row(
                children: [
                  Expanded(
                    child: Wrap(
                      spacing: 4, runSpacing: 4,
                      children: [
                        if (repo.techStack.isNotEmpty)
                          ...repo.techStack.take(2).map((tech) => _buildTechChip(tech))
                        else if (repo.language.isNotEmpty)
                          _buildTechChip(repo.language),
                      ],
                    ),
                  ),
                  InkWell(
                    onTap: () => _launchUrl(_githubService.getCollaborationUrl(repo.htmlUrl)),
                    borderRadius: BorderRadius.circular(8),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        border: Border.all(color: _kGreen.withOpacity(0.5)),
                        borderRadius: BorderRadius.circular(8),
                        color: _kGreen.withOpacity(0.1),
                      ),
                      child: Row(mainAxisSize: MainAxisSize.min, children: [
                        Icon(Icons.person_add_alt_1, size: 13, color: _kGreen),
                        const SizedBox(width: 5),
                        Text('Join', style: GoogleFonts.inter(color: _kGreen, fontSize: 11, fontWeight: FontWeight.w600)),
                      ]),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildGradeBadge(String grade) {
    final color = _gradeColor(grade);
    return Container(
      width: 36, height: 36,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color.withOpacity(0.15),
        border: Border.all(color: color, width: 1.5),
      ),
      child: Center(
        child: Text(grade, style: GoogleFonts.outfit(color: color, fontSize: 11, fontWeight: FontWeight.w800)),
      ),
    );
  }

  Widget _buildQualityBar(double score) {
    final color = score >= 80 ? const Color(0xFF00E676) : score >= 65 ? const Color(0xFF40C4FF) : score >= 50 ? _kGold : Colors.redAccent;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Quality', style: GoogleFonts.inter(color: _kTextSecondary, fontSize: 10)),
            Text('${score.toStringAsFixed(0)}/100', style: GoogleFonts.inter(color: color, fontSize: 10, fontWeight: FontWeight.w600)),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: score / 100,
            backgroundColor: _kBgCardLight,
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 4,
          ),
        ),
      ],
    );
  }

  Widget _buildStatBadge(IconData icon, String label, Color color) {
    return Row(mainAxisSize: MainAxisSize.min, children: [
      Icon(icon, size: 13, color: color),
      const SizedBox(width: 3),
      Text(label, style: GoogleFonts.inter(color: _kTextSecondary, fontSize: 11, fontWeight: FontWeight.w500)),
    ]);
  }

  Widget _buildTechChip(String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: _kGreen.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: _kGreen.withOpacity(0.3)),
      ),
      child: Text(label, style: GoogleFonts.inter(color: _kGreen, fontSize: 10)),
    );
  }

  Widget _buildAvatar(double radius) {
    final displayName = _user?.displayName ?? _userData?['name'] ?? 'User';
    final initial = displayName.isNotEmpty ? displayName[0].toUpperCase() : 'U';
    final photoBase64 = _userData?['photo_base64'];
    final photoUrl = _user?.photoURL ?? _userData?['photo_url'];

    return CircleAvatar(
      radius: radius,
      backgroundColor: _kGreen,
      child: ClipOval(
        child: photoBase64 != null
            ? Image.memory(base64Decode(photoBase64), fit: BoxFit.cover, width: radius * 2, height: radius * 2,
                errorBuilder: (c, e, s) => _initialsWidget(initial))
            : photoUrl != null
                ? Image.network(photoUrl, fit: BoxFit.cover, width: radius * 2, height: radius * 2,
                    errorBuilder: (c, e, s) => _initialsWidget(initial))
                : _initialsWidget(initial),
      ),
    );
  }

  Widget _initialsWidget(String initial) {
    return Center(
      child: Text(initial, style: GoogleFonts.outfit(color: _kBgDark, fontWeight: FontWeight.bold, fontSize: 14)),
    );
  }
}
