import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:hacker/models/github_repo.dart';
import 'package:flutter/foundation.dart';

class GithubService {
  static const String _backendUrl = 'http://localhost:8000';

  Future<List<GithubRepo>> searchRepositories(
    String query, {
    String? techStack,
    String? status,
    int minStars = 0,
    int? maxStars,
    int minForks = 0,
    int? maxQualityScore,
    int minQualityScore = 0,
    String? sortBy,        // 'updated', 'stars', 'forks', 'quality'
    bool excludeForks = false,
    bool excludeArchived = false,
    String? createdAfter,  // YYYY-MM-DD
    String? languages,     // comma-separated e.g. "Python,JavaScript"
  }) async {
    try {
      final queryParameters = <String, String>{
        'q': query,
        'min_stars': minStars.toString(),
        'min_quality_score': minQualityScore.toString(),
        'exclude_forks': excludeForks.toString(),
        'exclude_archived': excludeArchived.toString(),
      };

      if (status != null) queryParameters['status'] = status;
      if (techStack != null) queryParameters['tech_stack'] = techStack;
      if (maxStars != null) queryParameters['max_stars'] = maxStars.toString();
      if (minForks > 0) queryParameters['min_forks'] = minForks.toString();
      if (sortBy != null) queryParameters['sort_by'] = sortBy;
      if (createdAfter != null) queryParameters['created_after'] = createdAfter;
      if (languages != null) queryParameters['languages'] = languages;

      final uri = Uri.parse('$_backendUrl/search').replace(queryParameters: queryParameters);
      debugPrint('Fetching from Backend: $uri');

      final response = await http.get(uri);

      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        return data.map((json) => GithubRepo.fromJson(json)).toList();
      } else {
        debugPrint('Backend Error: ${response.statusCode} ${response.body}');
        throw Exception('Failed to load repositories. Ensure Python server is running on port 8000.');
      }
    } catch (e) {
      debugPrint('Error fetching repos: $e');
      rethrow;
    }
  }

  Future<List<GithubRepo>> getTrending({String? category}) async {
    try {
      final uri = Uri.parse('$_backendUrl/trending').replace(queryParameters: {
        if (category != null) 'category': category,
        'limit': '20',
      });
      final response = await http.get(uri);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final List<dynamic> repos = data['repos'] ?? [];
        // Trending returns simplified structure, adapt it
        return repos.map((r) => GithubRepo(
          name: r['name']?.split('/')?.last ?? r['name'] ?? '',
          fullName: r['name'] ?? '',
          description: r['description'] ?? '',
          stars: r['stars'] ?? 0,
          forks: 0,
          language: r['language'] ?? '',
          htmlUrl: r['html_url'] ?? '',
          updatedAt: DateTime.now(),
          createdAt: DateTime.now(),
          openIssuesCount: 0,
        )).toList();
      } else {
        throw Exception('Failed to load trending repos');
      }
    } catch (e) {
      debugPrint('Error fetching trending: $e');
      rethrow;
    }
  }

  /// Generates a URL to create a new issue for collaboration
  String getCollaborationUrl(String repoHtmlUrl) {
    return '$repoHtmlUrl/issues/new?title=Collaboration+Request&body=Hi,+I+am+interested+in+collaborating+on+this+project!';
  }
}
