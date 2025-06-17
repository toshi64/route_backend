from rest_framework import serializers
from .models import QuestionClipForGrammar, GrammarQuestion, AnswerUnit, AIFeedback
from instant_feedback.models import Session
from material_scheduler.models import ScheduleComponent

class QuestionClipForGrammarSerializer(serializers.ModelSerializer):
    answer_unit_id = serializers.IntegerField(write_only=True)
    grammar_question_id = serializers.IntegerField(required=False, write_only=True)

    class Meta:
        model = QuestionClipForGrammar
        fields = [
            'id', 'user', 'answer_unit_id', 'grammar_question_id',
            'content', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user

        # 必須：AnswerUnit を取得
        answer_unit_id = validated_data.pop('answer_unit_id')
        answer_unit = AnswerUnit.objects.get(id=answer_unit_id)

        # 任意：GrammarQuestion を取得
        grammar_question = None
        if 'grammar_question_id' in validated_data:
            grammar_question_id = validated_data.pop('grammar_question_id')
            grammar_question = GrammarQuestion.objects.filter(id=grammar_question_id).first()

        # 関連情報を AnswerUnit から引く
        session = answer_unit.session
        schedule_component = answer_unit.component

        return QuestionClipForGrammar.objects.create(
            user=user,
            answer_unit=answer_unit,
            grammar_question=grammar_question,
            session=session,
            schedule_component=schedule_component,
            **validated_data
        )





# GrammarQuestion（問題文、ジャンル、模範解答）
class GrammarQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarQuestion
        fields = ['id', 'question_text', 'genre', 'subgenre', 'answer']

# AIFeedback（AIのフィードバック）
class AIFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIFeedback
        fields = ['feedback_text']

# AnswerUnit（ユーザーの回答、紐づくGrammarQuestionとAI Feedbackを含む）
class AnswerUnitSerializer(serializers.ModelSerializer):
    question = GrammarQuestionSerializer()
    ai_feedback = AIFeedbackSerializer()

    class Meta:
        model = AnswerUnit
        fields = ['id', 'user_answer', 'created_at', 'question', 'ai_feedback']

# QuestionClipForGrammar（疑問clipのメイン）
class QuestionClipDetailSerializer(serializers.ModelSerializer):
    answer_unit = AnswerUnitSerializer()

    class Meta:
        model = QuestionClipForGrammar
        fields = ['id', 'content', 'created_at', 'answer_unit']



class ReviewCandidateSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source='question.id')
    question_text = serializers.CharField(source='question.question_text')
    genre = serializers.CharField(source='question.genre')
    subgenre = serializers.CharField(source='question.subgenre')  # ✅ これを追加
    difficulty = serializers.IntegerField(source='question.difficulty')
    created_at = serializers.DateTimeField()

    class Meta:
        model = AnswerUnit
        fields = ['question_id', 'question_text', 'genre', 'subgenre', 'difficulty', 'created_at']
