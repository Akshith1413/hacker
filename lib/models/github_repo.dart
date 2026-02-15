class QualityDetail {
  final double totalScore;
  final double documentationScore;
  final double codeQualityScore;
  final double communityScore;
  final double maintenanceScore;
  final String grade;

  QualityDetail({
    required this.totalScore,
    required this.documentationScore,
    required this.codeQualityScore,
    required this.communityScore,
    required this.maintenanceScore,
    required this.grade,
  });

  factory QualityDetail.fromJson(Map<String, dynamic> json) {
    return QualityDetail(
      totalScore: (json['total_score'] ?? 0).toDouble(),
      documentationScore: (json['documentation_score'] ?? 0).toDouble(),
      codeQualityScore: (json['code_quality_score'] ?? 0).toDouble(),
      communityScore: (json['community_score'] ?? 0).toDouble(),
      maintenanceScore: (json['maintenance_score'] ?? 0).toDouble(),
      grade: json['grade'] ?? 'F',
    );
  }
}

class TechStackConfidence {
  final String name;
  final double confidence;

  TechStackConfidence({required this.name, required this.confidence});

  factory TechStackConfidence.fromJson(Map<String, dynamic> json) {
    return TechStackConfidence(
      name: json['name'] ?? '',
      confidence: (json['confidence'] ?? 0).toDouble(),
    );
  }
}

class GithubRepo {
  final String name;
  final String fullName;
  final String description;
  final int stars;
  final int forks;
  final String language;
  final String htmlUrl;
  final DateTime updatedAt;
  final DateTime createdAt;
  final int openIssuesCount;
  final String? ownerAvatarUrl;

  // ML Fields
  final String? status;
  final List<String> techStack;
  final double? qualityScore;
  final QualityDetail? qualityDetail;
  final List<TechStackConfidence> techStackConfidence;

  GithubRepo({
    required this.name,
    required this.fullName,
    required this.description,
    required this.stars,
    required this.forks,
    required this.language,
    required this.htmlUrl,
    required this.updatedAt,
    required this.createdAt,
    required this.openIssuesCount,
    this.ownerAvatarUrl,
    this.status,
    this.techStack = const [],
    this.qualityScore,
    this.qualityDetail,
    this.techStackConfidence = const [],
  });

  factory GithubRepo.fromJson(Map<String, dynamic> json) {
    // Handle avatar: backend sends flat 'owner_avatar_url', GitHub sends nested 'owner.avatar_url'
    String? avatarUrl = json['owner_avatar_url'];
    if (avatarUrl == null && json['owner'] != null) {
      avatarUrl = json['owner']['avatar_url'];
    }

    return GithubRepo(
      name: json['name'] ?? 'Unknown',
      fullName: json['full_name'] ?? '',
      description: json['description'] ?? 'No description available.',
      stars: json['stars'] ?? json['stargazers_count'] ?? 0,
      forks: json['forks'] ?? json['forks_count'] ?? 0,
      language: json['language'] ?? 'Unknown',
      htmlUrl: json['html_url'] ?? '',
      updatedAt: DateTime.tryParse(json['updated_at'] ?? '') ?? DateTime.now(),
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
      openIssuesCount: json['open_issues_count'] ?? 0,
      ownerAvatarUrl: avatarUrl,
      status: json['status'],
      techStack: (json['tech_stack'] as List<dynamic>?)?.map((e) => e.toString()).toList() ?? [],
      qualityScore: json['quality_score'] != null ? (json['quality_score'] as num).toDouble() : null,
      qualityDetail: json['quality_detail'] != null ? QualityDetail.fromJson(json['quality_detail']) : null,
      techStackConfidence: (json['tech_stack_confidence'] as List<dynamic>?)
              ?.map((e) => TechStackConfidence.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
    );
  }

  /// Returns a color-coded grade color string
  String get gradeLabel => qualityDetail?.grade ?? '–';

  /// Returns a human-readable quality tier
  String get qualityTier {
    final score = qualityScore ?? 0;
    if (score >= 80) return 'Excellent';
    if (score >= 65) return 'Good';
    if (score >= 50) return 'Fair';
    return 'Poor';
  }
}
