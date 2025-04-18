# HotLabel - Crowdsourced Data Labeling Solution

HotLabel is an innovative platform that replaces intrusive online advertising with micro data-labeling tasks, creating a win-win solution for website monetization and AI training. The system transforms disruptive pop-up ads into brief, valuable interactions that generate high-quality human labels for LLM alignment at significantly lower costs than traditional methods.

## Core Concept

Instead of forcing users to engage with annoying advertisements, HotLabel introduces a data-labeling task window that replaces pop-ups while generating significantly higher revenue per interaction. This system capitalizes on the demand for high-quality labeled data, which is essential for training artificial intelligence (AI) models in fields like computer vision, natural language processing, and autonomous systems.

## Technical Architecture

HotLabel is built as a monolithic FastAPI application that integrates four core services:

1. **Task Management Service** - Distributes appropriate labeling tasks to users
2. **User Profiling Service** - Learns about user expertise and language capabilities
3. **Quality Assurance Service** - Ensures high-quality labels through validation techniques
4. **Publisher Management Service** - Manages publisher relationships and configurations

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/hotlabel.git
   cd hotlabel
   ```

2. Create a `.env` file based on the example:
   ```bash
   cp .env.example .env
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Access the API documentation:
   ```
   http://localhost:8000/docs
   ```

## Development

### Running Tests

```bash
docker-compose exec api pytest
```

### Database Migrations

```bash
docker-compose exec api alembic upgrade head
```

## Deployment

For production deployment, please refer to the [deployment guide](docs/deployment.md).

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.