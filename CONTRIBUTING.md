# Contributing Guide

Thank you for considering contributing to TikTok Scraper!

## Code of Conduct

- Be respectful and inclusive
- Follow ethical scraping practices
- Respect TikTok's Terms of Service
- Do not use for malicious purposes

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/tiktok-scraper.git
   cd tiktok-scraper
   ```
3. **Create a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```
4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```
5. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

We follow PEP 8 style guide. Use these tools:

```bash
# Format code
black app/ tests/

# Check linting
flake8 app/ tests/

# Type checking
mypy app/
```

### Testing

Write tests for new features:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_scrapers.py

# Run with coverage
pytest --cov=app tests/
```

### Commit Messages

Follow conventional commits:

```
feat: add hashtag search pagination
fix: resolve video download timeout issue
docs: update API documentation
test: add tests for profile scraper
refactor: improve error handling in downloader
```

## Areas for Contribution

### High Priority

1. **Scraping Improvements**
   - Handle TikTok structure changes
   - Improve Playwright scraping efficiency
   - Add support for more data extraction

2. **Download Enhancements**
   - Better no-watermark methods
   - Support for different video qualities
   - Resume interrupted downloads

3. **Storage Options**
   - Add support for AWS S3
   - Add support for Azure Blob Storage
   - Local storage improvements

4. **Performance**
   - Optimize database queries
   - Improve concurrent download handling
   - Reduce memory usage

### Medium Priority

5. **Features**
   - Video search by keywords
   - User analytics dashboard
   - Export to different formats
   - Duplicate detection

6. **UI/UX**
   - Improve Streamlit dashboard
   - Add React frontend option
   - Mobile-responsive design

7. **Monitoring**
   - Add Prometheus metrics
   - Grafana dashboards
   - Alert system

### Low Priority

8. **Documentation**
   - Video tutorials
   - More examples
   - Translation to other languages

9. **Testing**
   - Integration tests
   - End-to-end tests
   - Load testing

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
   ```bash
   pytest tests/
   ```
4. **Update CHANGELOG.md**
5. **Create pull request** with clear description
6. **Wait for review** and address feedback

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## Reporting Issues

### Bug Reports

Include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Logs/screenshots

### Feature Requests

Include:
- Clear use case
- Proposed solution
- Alternative solutions considered
- Additional context

## Code Review Guidelines

Reviewers will check:
- Code quality and style
- Test coverage
- Documentation
- Performance impact
- Security considerations

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open an issue for questions
- Join our discussions
- Check existing issues/PRs first

## Recognition

Contributors will be added to:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing! 🎉
