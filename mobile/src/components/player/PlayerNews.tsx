import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, Linking, StyleSheet, ActivityIndicator } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { theme } from '../../constants/theme';
import { apiService } from '../../services/api';

interface NewsArticle {
    title: string;
    url: string;
    source: string;
    published_at: string;
}

interface PlayerNewsProps {
    playerName: string;
}

export const PlayerNews: React.FC<PlayerNewsProps> = ({ playerName }) => {
    const [news, setNews] = useState<NewsArticle[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        let mounted = true;

        const fetchNews = async () => {
            if (!playerName) return;

            try {
                setLoading(true);
                setError(false);
                const data = await apiService.getPlayerNews(playerName, 4);
                if (mounted) {
                    setNews(data);
                }
            } catch (err) {
                console.error("Failed to load news", err);
                if (mounted) setError(true);
            } finally {
                if (mounted) setLoading(false);
            }
        };

        fetchNews();
        return () => { mounted = false; };
    }, [playerName]);

    const handlePress = (url: string) => {
        Linking.openURL(url).catch(err => console.error("Couldn't load page", err));
    };

    const formatTime = (isoString: string) => {
        if (!isoString) return '';
        const date = new Date(isoString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));

        if (diffHrs < 1) return 'Just now';
        if (diffHrs < 24) return `${diffHrs}h ago`;
        return `${Math.floor(diffHrs / 24)}d ago`;
    };

    if (loading) {
        return (
            <View style={styles.container}>
                <View style={styles.headerRow}>
                    <View style={styles.titleContainer}>
                        <Ionicons name="newspaper-outline" size={18} color={theme.colors.primary} />
                        <Text style={styles.headerTitle}>Recent News</Text>
                    </View>
                </View>
                <View style={styles.loaderContainer}>
                    <ActivityIndicator size="small" color={theme.colors.primary} />
                </View>
            </View>
        );
    }

    if (error || news.length === 0) {
        return null;
    }

    return (
        <View style={styles.container}>
            <View style={styles.headerRow}>
                <View style={styles.titleContainer}>
                    <Ionicons name="newspaper-outline" size={18} color={theme.colors.primary} />
                    <Text style={styles.headerTitle}>Recent News</Text>
                </View>
            </View>

            <View style={styles.list}>
                {news.map((item, index) => (
                    <TouchableOpacity
                        key={index}
                        style={[styles.newsItem, index === news.length - 1 && styles.lastItem]}
                        onPress={() => handlePress(item.url)}
                        activeOpacity={0.7}
                    >
                        <View style={styles.newsContent}>
                            <Text style={styles.newsSource}>
                                {item.source} {item.published_at ? `\u2022 ${formatTime(item.published_at)}` : ''}
                            </Text>
                            <Text style={styles.newsTitle} numberOfLines={2}>
                                {item.title}
                            </Text>
                        </View>
                        <Ionicons name="chevron-forward" size={16} color={theme.colors.textTertiary} />
                    </TouchableOpacity>
                ))}
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        backgroundColor: theme.colors.backgroundCard,
        borderRadius: theme.borderRadius.m,
        borderWidth: 1,
        borderColor: theme.colors.glassBorder,
        padding: 16,
        marginVertical: 6,
    },
    headerRow: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 12,
    },
    titleContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 8,
    },
    headerTitle: {
        fontSize: 16,
        fontWeight: '700',
        color: theme.colors.textPrimary,
    },
    loaderContainer: {
        padding: 16,
        alignItems: 'center',
    },
    list: {
        gap: 0,
    },
    newsItem: {
        paddingVertical: 10,
        borderBottomWidth: 1,
        borderBottomColor: theme.colors.glassBorder,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
    },
    lastItem: {
        borderBottomWidth: 0,
        paddingBottom: 0,
    },
    newsContent: {
        flex: 1,
        paddingRight: 12,
    },
    newsSource: {
        fontSize: 11,
        color: theme.colors.textTertiary,
        marginBottom: 3,
        fontWeight: '500',
    },
    newsTitle: {
        fontSize: 13,
        color: theme.colors.textSecondary,
        lineHeight: 18,
        fontWeight: '500',
    },
});
